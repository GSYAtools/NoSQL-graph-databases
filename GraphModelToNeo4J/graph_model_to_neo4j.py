
import os
import typer
import requests


endpoint = "https://khaos.uma.es/NoSQL/api/"
verbose = True


## final version with arguments
def GraphModelToNeo4J(
    database: str = typer.Option(..., help="Database name"),
    outputfile: str = typer.Option(..., help="Output file")
    ):

    # base URL for further queries with endpoint and database parameter 
    baseURL = endpoint + database + "/"
    
    # creates the output folder and file
    if(not os.path.exists("data")):
        os.makedirs("data")
    os.chdir("data")
    f = open(outputfile, "w")

    dbname = generateDatabase(baseURL)

    generateRoles(baseURL, dbname, f)

    generateUsers(baseURL, dbname, f)

    generateSecurityRuleElement(baseURL, dbname, f)

    generateSecurityRuleField(baseURL, dbname, f)

    f.close()
        

# -----------------------------------------
# Database
# -----------------------------------------
def generateDatabase(baseURL):
    URL = baseURL + "database"
    response = requests.get(URL) 
    data = response.json() 
    dbname = data[0]["DatabaseName"]["value"]
    if(verbose): print("\n\nDatabase: " + dbname + "\n")
    return dbname

# -----------------------------------------
# Roles
# -----------------------------------------
def generateRoles(baseURL, dbname, f):
    URL = baseURL + "roles" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json() 
    for element in data:
        value = element["RoleName"]["value"]
        if(verbose): print("Role: " + value)
        f.write("CREATE ROLE "+ value +";\n")

# -----------------------------------------
# Users
# -----------------------------------------
def generateUsers(baseURL, dbname,f):
    URL = baseURL + "users" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json()   
    for element in data:
        value = element["UserName"]["value"]
        if(verbose): print("\nUser: " + value)        
        f.write("CREATE USER " + value + ";\n")
    
        # grant role to users
        URL = baseURL + "rolesAssignedToUser" + "?user_name="+value
        response = requests.get(URL)
        data2 = response.json()
        for element2 in data2:
            value2 = element2["RoleName"]["value"]
            if(verbose): print("Role assigned: " + value2)     
            f.write("GRANT ROLE " + value2 + " TO "+value+";\n")



# -----------------------------------------
# Security Rules for Elements
# -----------------------------------------
def generateSecurityRuleElement(baseURL, dbname, f):
    URL = baseURL + "securityRuleElement" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json()   
    
    for rule in data:
        rulename = rule["ruleName"]["value"]
        if(verbose): print("\nSecurity Rule Element: " + rulename)        
        
        # get rule details
        URL = baseURL + "securityRuleElementDetails" + "?rule_name="+rulename
        response = requests.get(URL) 
        datadetails = response.json()
        # for atributes with cardinality 1..1
        sign = datadetails[0]["sign"]["value"]
        # for atributes with cardinality 1..n
        rolenameslist = obtainList(datadetails, "RoleName")
        privilegeslist = obtainList(datadetails, "privilege")
        
        if(verbose): 
            print("   Sign: " + sign) 
            print("   Roles: " + formatList(rolenameslist))
            print("   Privileges: " + formatList(privilegeslist))
            print("Security policies generated:")

        # create two security policies for each privilege
        # one for nodes and one for relationships
        for p in privilegeslist:
            securityPolicy = ""

            # sign
            if(sign=="+"): securityPolicy += "GRANT "
            else: securityPolicy += "DENY "
            
            # privilege
            if(p=="Read"): securityPolicy += "MATCH"
            elif(p=="Create"): securityPolicy += "CREATE"
            elif(p=="Delete"): securityPolicy += "DELETE"
            elif(p=="Update"): securityPolicy += "SET PROPERTY {*}"

            # graph
            securityPolicy += " ON GRAPH " + dbname

            # nodes
            generatePolicy(baseURL, rulename, rolenameslist, securityPolicy, True, False, f)

            # relationships
            generatePolicy(baseURL, rulename, rolenameslist, securityPolicy, False, False, f)


# -----------------------------------------
# Security Rules for Fields
# -----------------------------------------
def generateSecurityRuleField(baseURL, dbname, f):
    URL = baseURL + "securityRuleField" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json()   

    for rule in data:
        rulename = rule["ruleName"]["value"]
        if(verbose): print("\nSecurity Rule Field: " + rulename)        
        
        # get rule details
        URL = baseURL + "securityRuleFieldDetails" + "?rule_name="+rulename
        response = requests.get(URL) 
        datadetails = response.json()
        # for atributes with cardinality 1..1
        sign = datadetails[0]["sign"]["value"]
        # for optional attributes with cardinality 0..1 
        condition = ""
        if "condition" in datadetails[0]:
            condition = datadetails[0]["condition"]["value"]
        # for atributes with cardinality 1..n
        rolenameslist = obtainList(datadetails, "RoleName")
        privilegeslist = obtainList(datadetails, "privilege")
        fieldlist = obtainList(datadetails, "fieldName")

        if(verbose): 
            print("   Sign: " + sign) 
            print("   Roles: " + formatList(rolenameslist))
            print("   Privileges: " + formatList(privilegeslist))
            print("   Fields: " + formatList(fieldlist))
            print("   Condition: " + condition)
            print("Security policies generated:")

        # create two security policies for each privilege
        # one for nodes and one for relationships
        for p in privilegeslist:
            securityPolicy = ""

            # sign
            if(sign=="+"): securityPolicy += "GRANT "
            else: securityPolicy += "DENY "
            
            # privilege
            if(p=="Read"): securityPolicy += "MATCH"
            elif(p=="Create"): securityPolicy += "CREATE"
            elif(p=="Delete"): securityPolicy += "DELETE"
            elif(p=="Update"): securityPolicy += "SET PROPERTY {*}"

            # fields
            securityPolicy += " " + formatList(fieldlist)

            # graph
            securityPolicy += " ON GRAPH " + dbname

            # nodes
            generatePolicy(baseURL, rulename, rolenameslist, securityPolicy, True, True, f)

            # relationships
            generatePolicy(baseURL, rulename, rolenameslist, securityPolicy, False, True, f)


# Generates security policy and writes it in the output file
# get the starting part of the policy (previously generated) 
# attaches the elements involved
# - nodes or relationships (parameter nodes = true or false)
# - fields (consider fields if finegrain = true)
# attaches the list of roles
def generatePolicy(baseURL, rulename, rolenameslist, securityPolicy, nodes, finegrain, f):

    if (nodes):
        if (finegrain):
            URL = baseURL + "securityRuleFieldAssociatedNodes" + "?rule_name="+rulename
        else:
            URL = baseURL + "securityRuleElementAssociatedNodes" + "?rule_name="+rulename
    else:
        if (finegrain):
            URL = baseURL + "securityRuleFieldAssociatedRelationships" + "?rule_name="+rulename
        else:
            URL = baseURL + "securityRuleElementAssociatedRelationships" + "?rule_name="+rulename
          
    response = requests.get(URL) 
    dataelements = response.json()

    securityPolicyTmp = ""
    elementlist = obtainList(dataelements, "elementName")

    if(len(elementlist)==1):
        if (nodes):
            securityPolicyTmp += " NODE "
        else:
            securityPolicyTmp += " RELATIONSHIP "
        securityPolicyTmp += elementlist[0]
    elif(len(elementlist)>1): 
        if (nodes):
            securityPolicyTmp += " NODES "
        else:
            securityPolicyTmp += " RELATIONSHIPS "
        securityPolicyTmp += formatList(elementlist)
    
    if(len(elementlist)>0):
        securityPolicyTmp += " TO " + formatList(rolenameslist) + ";"           
        f.write(securityPolicy + securityPolicyTmp + "\n")
        if(verbose): print(securityPolicy + securityPolicyTmp)


# processes a json text to obtain a list with values for a tag "str"
def obtainList(datadetails, str):        
    list = []
    # extract values
    for d in datadetails:
        list.append(d[str]["value"])
    # remove duplicates
    list = sorted(set(list))
    return list

# formats a list as a string with items separed with ,
def formatList(list):
    listformatted = ""
    first = True
    for n in list:
        if(first):
            listformatted += n
            first = False
        else:    
            listformatted += ", " + n
    return listformatted


if __name__ == "__main__":
    typer.run(GraphModelToNeo4J)



