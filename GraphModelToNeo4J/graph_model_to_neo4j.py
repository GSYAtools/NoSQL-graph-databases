
import os
import typer
import requests


## final version with arguments
#def GraphModelToNeo4J(
#    database: str = typer.Option(..., help="Database name"),
#    outputfile: str = typer.Option(..., help="Output file")
#    ):



## for testing without arguments
def GraphModelToNeo4J():
    database = "NoSQL-Aeropuerto"
    #database = "NoSQL-Hospital"
    #database = "NoSQL-RedSocial"
    outputfile = "output.txt"

# configuration
    verbose = True
    os.chdir("data")
    endpoint = "https://khaos.uma.es/NoSQL/api/"
    baseURL = endpoint + database + "/"
    f = open(outputfile, "w")


# -----------------------------------------
# Database, Roles and Users
# -----------------------------------------

# database
    URL = baseURL + "database"
    response = requests.get(URL) 
    data = response.json() 
    dbname = data[0]["DatabaseName"]["value"]
    if(verbose): print("Database: " + dbname)

# roles
    URL = baseURL + "roles" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json() 
    for element in data:
        value = element["RoleName"]["value"]
        if(verbose): print("Role: " + value)
        f.write("CREATE ROLE "+ value +";\n")

# users
    URL = baseURL + "users" + "?database_name="+dbname
    response = requests.get(URL) 
    data = response.json()   
    for element in data:
        value = element["UserName"]["value"]
        if(verbose): print("User: " + value)        
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
        rolenameslist = []
        privilegeslist = []
        for d in datadetails:
            rolenameslist.append(d["RoleName"]["value"])
            privilegeslist.append(d["privilege"]["value"])
        # remove duplicates
        rolenameslist = sorted(set(rolenameslist))
        privilegeslist = sorted(set(privilegeslist))
        # format role list separated with ,
        rolenameslistformatted = ""
        first = True
        for n in rolenameslist:
            if(first):
                rolenameslistformatted += n
                first = False
            else:    
                rolenameslistformatted += ", " + n

        if(verbose): 
            print(" Details:")
            print("   Sign: " + sign) 
            print("   Roles:")
            print(rolenameslist)
            print("   Privileges:")
            print(privilegeslist)   

        # create two security policies for each privilege
        # one for nodes and one for relationships
        for p in privilegeslist:
            securityPolicy = ""
        
            if(sign=="+"): securityPolicy += "GRANT "
            else: securityPolicy += "DENY "
        
            if(p=="Read"): securityPolicy += "MATCH"
            elif(p=="Create"): securityPolicy += "CREATE"
            elif(p=="Delete"): securityPolicy += "DELETE"
            elif(p=="Update"): securityPolicy += "SET PROPERTY {*}"
            securityPolicy += " ON GRAPH " + dbname

            # nodes
            URL = baseURL + "securityRuleElementAssociatedNodes" + "?rule_name="+rulename
            response = requests.get(URL) 
            dataelements = response.json()

            securityPolicyTmp = ""
            elementlist = []
            for n in dataelements:
                elementlist.append(n["elementName"]["value"])
            elementlist = sorted(set(elementlist))

            if(len(elementlist)==1):
                securityPolicyTmp += " NODE " + elementlist[0]
            elif(len(elementlist)>1): 
                securityPolicyTmp += " NODES "
                first = True
                for n in elementlist:
                    if(first):
                        securityPolicyTmp += n
                        first = False
                    else:    
                        securityPolicyTmp += ", " + n
            if(len(elementlist)>0):
                securityPolicyTmp += " TO " + rolenameslistformatted + ";\n"
                f.write(securityPolicy + securityPolicyTmp)
                if(verbose): print(securityPolicy + securityPolicyTmp)
                securityPolicyTmp = ""
               
            
            # relationships    
            URL = baseURL + "securityRuleElementAssociatedRelationships" + "?rule_name="+rulename
            response = requests.get(URL) 
            dataelements = response.json()

            securityPolicyTmp = ""
            elementlist = []
            for n in dataelements:
                elementlist.append(n["elementName"]["value"])
            elementlist = sorted(set(elementlist))

            if(len(elementlist)==1):
                securityPolicyTmp += " RELATIONSHIP " + elementlist[0]
            elif(len(elementlist)>1): 
                securityPolicyTmp += " RELATIONSHIPS "
                first = True
                for n in elementlist:
                    if(first):
                        securityPolicyTmp += n
                        first = False
                    else:    
                        securityPolicyTmp += ", " + n
            if(len(elementlist)>0):
                securityPolicyTmp += " TO " + rolenameslistformatted + ";\n"
                f.write(securityPolicy + securityPolicyTmp)
                if(verbose): print(securityPolicy + securityPolicyTmp)
                securityPolicyTmp = ""



# -----------------------------------------
# Security Rules for Fields
# -----------------------------------------
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
        rolenameslist = []
        privilegeslist = []
        fieldlist = []
        for d in datadetails:
            rolenameslist.append(d["RoleName"]["value"])
            privilegeslist.append(d["privilege"]["value"])
            fieldlist.append(d["fieldName"]["value"])
        # remove duplicates
        rolenameslist = sorted(set(rolenameslist))
        privilegeslist = sorted(set(privilegeslist))
        fieldlist = sorted(set(fieldlist))
        # format role list separated with ,
        rolenameslistformatted = ""
        first = True
        for n in rolenameslist:
            if(first):
                rolenameslistformatted += n
                first = False
            else:    
                rolenameslistformatted += ", " + n
        # format field list separated with ,
        fieldlistformatted = ""
        first = True
        for n in fieldlist:
            if(first):
                fieldlistformatted += n
                first = False
            else:    
                fieldlistformatted += ", " + n

        if(verbose): 
            print(" Details:")
            print("   Sign: " + sign) 
            print("   Roles:" + rolenameslistformatted)
            print("   Privileges:")
            print(privilegeslist)   
            print("   Fields:" + fieldlistformatted)
            print("   Condition:" + condition)

        # create two security policies for each privilege
        # one for nodes and one for relationships
        for p in privilegeslist:
            securityPolicy = ""
        
            if(sign=="+"): securityPolicy += "GRANT "
            else: securityPolicy += "DENY "
        
            if(p=="Read"): securityPolicy += "MATCH"
            elif(p=="Create"): securityPolicy += "CREATE"
            elif(p=="Delete"): securityPolicy += "DELETE"
            elif(p=="Update"): securityPolicy += "SET PROPERTY {*}"
            
            securityPolicy += " " + fieldlistformatted

            securityPolicy += " ON GRAPH " + dbname

            # nodes
            URL = baseURL + "securityRuleFieldAssociatedNodes" + "?rule_name="+rulename
            response = requests.get(URL) 
            dataelements = response.json()

            securityPolicyTmp = ""
            elementlist = []
            for n in dataelements:
                elementlist.append(n["elementName"]["value"])
            elementlist = sorted(set(elementlist))

            if(len(elementlist)==1):
                securityPolicyTmp += " NODE " + elementlist[0]
            elif(len(elementlist)>1): 
                securityPolicyTmp += " NODES "
                first = True
                for n in elementlist:
                    if(first):
                        securityPolicyTmp += n
                        first = False
                    else:    
                        securityPolicyTmp += ", " + n
            if(len(elementlist)>0):
                securityPolicyTmp += " TO " + rolenameslistformatted + ";\n"
                f.write(securityPolicy + securityPolicyTmp)
                if(verbose): print(securityPolicy + securityPolicyTmp)
                securityPolicyTmp = ""
               

            # relationships    
            URL = baseURL + "securityRuleFieldAssociatedRelationships" + "?rule_name="+rulename
            response = requests.get(URL) 
            dataelements = response.json()

            securityPolicyTmp = ""
            elementlist = []
            for n in dataelements:
                elementlist.append(n["elementName"]["value"])
            elementlist = sorted(set(elementlist))

            if(len(elementlist)==1):
                securityPolicyTmp += " RELATIONSHIP " + elementlist[0]
            elif(len(elementlist)>1): 
                securityPolicyTmp += " RELATIONSHIPS "
                first = True
                for n in elementlist:
                    if(first):
                        securityPolicyTmp += n
                        first = False
                    else:    
                        securityPolicyTmp += ", " + n
            if(len(elementlist)>0):
                securityPolicyTmp += " TO " + rolenameslistformatted + ";\n"
                f.write(securityPolicy + securityPolicyTmp)
                if(verbose): print(securityPolicy + securityPolicyTmp)
                securityPolicyTmp = ""



# close
    f.close()
        
if __name__ == "__main__":
    typer.run(GraphModelToNeo4J)