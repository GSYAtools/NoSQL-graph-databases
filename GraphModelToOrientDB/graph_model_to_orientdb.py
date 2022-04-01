
import os
import typer
import requests


endpoint = "https://khaos.uma.es/NoSQL/api/"
verbose = True


## final version with arguments
def GraphModelToOrientDB(
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
        f.write("INSERT INTO ORole SET name = '"+ value + "', mode = 0;\n")

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
        f.write("INSERT INTO OUser SET name = '"+ value + 
        "', password = 'pass', status = 'ACTIVE', "+
        "roles = (SELECT FROM ORole WHERE name = ")

        # grant role to users
        URL = baseURL + "rolesAssignedToUser" + "?user_name="+value
        response = requests.get(URL)
        data2 = response.json()
        first = True
        for element2 in data2:
            value2 = element2["RoleName"]["value"]
            if(verbose): print("Role assigned: " + value2)     
            if(first):
                f.write("'" + value2 + "'")
                first = False
            else:
                f.write(" OR '" + value2 + "'")
        f.write(");\n")


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
        elementlist = obtainList(datadetails, "elementName")

        if(verbose): 
            print("   Sign: " + sign) 
            print("   Roles: " + formatList(rolenameslist))
            print("   Privileges: " + formatList(privilegeslist))
            print("   Elements: " + formatList(elementlist))
            print("Security policies generated:")

        # create a security policy for each element and role
        for e in elementlist:
            for r in rolenameslist:
                securityPolicy = ""

                # sign
                if(sign=="+"): securityPolicy += "GRANT "
                else: securityPolicy += "REVOKE "
                
                # privilege
                securityPolicy += "SET "
                first = True
                for p in privilegeslist:
                    if(first == False):
                        securityPolicy += ", "
                    elif(first == True):
                        first = False

                    if(p=="Read"): securityPolicy += "READ"
                    elif(p=="Create"): securityPolicy += "CREATE"
                    elif(p=="Delete"): securityPolicy += "DELETE"
                    elif(p=="Update"): securityPolicy += "AFTER UPDATE"

                # element
                securityPolicy += " ON database.class." + e

                # role
                securityPolicy += " TO " + r

                # write
                if(verbose):
                    print("   " +securityPolicy)
                f.write(securityPolicy + ";\n")
                


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

        # create a security policy for each element and role
        for field in fieldlist:
            for r in rolenameslist:
                securityPolicy = ""

                # sign
                if(sign=="+"): securityPolicy += "GRANT "
                else: securityPolicy += "REVOKE "
                
                # privilege
                securityPolicy += "SET "
                first = True
                for p in privilegeslist:
                    if(first == False):
                        securityPolicy += ", "
                    elif(first == True):
                        first = False

                    if(p=="Read"): securityPolicy += "READ"
                    elif(p=="Create"): securityPolicy += "CREATE"
                    elif(p=="Delete"): securityPolicy += "DELETE"
                    elif(p=="Update"): securityPolicy += "AFTER UPDATE"

                    if condition:
                        securityPolicy += "=(" + condition + ")"

                # element
                securityPolicy += " ON database.class." + field

                # role
                securityPolicy += " TO " + r

                # write
                if(verbose):
                    print("   " +securityPolicy)
                f.write(securityPolicy + ";\n")
                







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
    typer.run(GraphModelToOrientDB)



