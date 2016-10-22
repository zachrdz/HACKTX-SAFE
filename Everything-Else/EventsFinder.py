import keys
import urllib.request
import json
import codecs

#list1 is a list of a list of strings, where each element in the original list is
#the list of elements
#each element's list's elements are as follows: (All elements in array are string)
#(title, date, coordinates, disaster type, description, affected countries)

def getEvents(list1):
    s = "https://api.sigimera.org/v1/crises?auth_token="
    s+= keys.sigimeraAuth()
    webUrl  = urllib.request.urlopen(s)
    if(webUrl.getcode() == 200):
        counter = 0
        response = webUrl.read().decode('utf-8')
        theJSON = json.loads(response)
        for i in theJSON:
            try:
                list1.index(i)
            except:
                counter+=1
            if(counter!=0):
                list2 = []
                list2.append(i["dc_title"])
                list2.append(i["dct_modified"])
                s = str(i["foaf_based_near"][1]) + " , " + str(i["foaf_based_near"][0])
                list2.append(s)
                list2.append(i["dc_subject"][0])
                list2.append(i["dc_description"])
                k = ""
                if(i["gn_parentCountry"]!=" "):
                    for j in i["gn_parentCountry"]:
                        k+=str(i["gn_parentCountry"])
                    list2.append(k)
                else:
                    list2.append("N/A, no affected countries")
                list1.append(list2)
        return list1
