
from .models import (Source, Work, Contributor)
import pandas as pd 
from similarity.jarowinkler import JaroWinkler
jarowinkler = JaroWinkler()

def worksManager(csv):
    """  
    Main Function To Manage all operation
    @param csv {File} a csv file with work_metadata format
    Priority
        * Check Match By ISWC
        * Check Match By Title
        * Validate Similarity of Titles
        * Check Existence of Contributors
        * Check Similarity of Contributors
    In case of Data Confilcts Saves the Source with Descriptive Status
        * ISWC Conflict
        * Title Conflict
        * Contributors Updated
        * New Work 
    """
    df = pd.read_csv(csv)
    for row in df.iterrows():
        work = row[1]
        iswc = work["iswc"]
        title = work["title"]
        contributors = work["contributors"].split('|')
        source = work["source"]
        sourceid = work["id"]
        worksByIswc = Work.objects.all().filter(iswc=iswc)
        
        if worksByIswc:
            print("ISWC {} already exist".format(iswc))
            if (validateStringSimilarity(worksByIswc[0].title,title) > 0.9):
                print("Title '{}' Validated".format(title))
                contributorByWork = Contributor.objects.all().filter(work=worksByIswc[0].id)
                if contributorByWork:
                    print("Previous Contributors. Compare Contributors")
                    prevContributors = [x.name for x in contributorByWork]
                    newContributors = []
                    for prevContributor in prevContributors:
                        for contributor in contributors:
                            sameContributor = validateContributorsSimilarity(prevContributor,contributor)
                            if (sameContributor or contributor in newContributors or contributor in prevContributors):
                                pass
                            else:
                                newContributors.append(contributor)
                    saveContributors(newContributors,worksByIswc[0])
                    newSource = Source(name=source, source_id=sourceid, status="Contributors Updated",work=worksByIswc[0])
                    newSource.save()
                else:
                    print("No Contributors, Insert {} new Contributors".format(contributors))
                    saveContributors(contributors,worksByIswc[0])
                    newSource = Source(name=source, source_id=sourceid, status="Contributors Updated",work=worksByIswc[0])
                    newSource.save()
            else:
                print("Diferent Title, Error Source: Title Conflict")
                newSource = Source(name=source, source_id=sourceid, status="Title Conflict", work=worksByIswc[0])
                newSource.save()
        else:
            worksByTitle = Work.objects.all().filter(title=title)
            if worksByTitle:
                print("Title {} already exist".format(title), worksByTitle[0].iswc)
                if (worksByTitle[0].iswc != 'nan' and worksByTitle[0].iswc != None):
                    print("Diferent ISWC, Error Source: ISWC Conflict")
                    newSource = Source(name=source, source_id=sourceid, status="ISWC Conflict", work=worksByTitle[0])
                    newSource.save()
                else:
                    print("Missing ISWC")
                    contributorByTitle = Contributor.objects.all().filter(work=worksByTitle[0].id)
                    if contributorByTitle:
                        print("Previous Contributors. Compare Contributors")
                        prevContributors = [x.name for x in contributorByTitle]
                        newContributors = []
                        for prevContributor in prevContributors:
                            for contributor in contributors:
                                sameContributor = validateContributorsSimilarity(prevContributor,contributor)
                                if (sameContributor or contributor in newContributors or contributor in prevContributors):
                                    pass
                                else:
                                    newContributors.append(contributor)
                        saveContributors(newContributors,worksByTitle[0])
                        newSource = Source(name=source, source_id=sourceid, status="Contributors Updated", work=worksByTitle[0])
                        newSource.save()
                        worksByTitle[0].iswc = iswc
                        worksByTitle[0].save()
                    else:
                        print("No Contributors, Insert {} new Contributors".format(contributors))
                        saveContributors(contributors,worksByTitle[0])
                        newSource = Source(name=source, source_id=sourceid, status="Contributors Updated", work=worksByTitle[0])
                        newSource.save()
                        worksByTitle[0].iswc = iswc
                        worksByTitle[0].save()
            else:
                print("No Match, add new work to catalogue")
                newWork = Work(title=title, iswc=iswc)
                newWork.save()
                saveContributors(contributors, newWork)
                newSource = Source(name=source, source_id=sourceid, status="New Work" ,work=newWork)
                newSource.save()
    return {"status": "Sucess"}

def validateStringSimilarity(inputTitle, actualTitle):
    """
    Function to calculate jarowinkler index of string similarity
    *@param inputTitle String    
    *@param actualTitle String
        Return an Integrer - Index 0-1 where 1 is a perfect match
    """
    value = jarowinkler.similarity(inputTitle.lower(), actualTitle.lower())
    return value

def contributorNameSimilarityIndex(lengthInput, lengthActual, lengthIntersection):
    """
    Function to calculate similiatiry beetwen two List of Names based on their common elements
    *@param lengthInput Integer    
    *@param lengthActual Integer
    *@param lengthIntersection Integer
        Return an Integrer - Index 0-1 where 1 is a perfect match
    """
    matchingReferecne = (lengthInput + lengthActual) / 2 
    return lengthIntersection / matchingReferecne

def validateContributorsSimilarity(inputContributor, actualContibutor):
    """
    Function to validate if two names correspond to the same person based on similarity of every element in their name
    *@param inputContributor String    
    *@param actualContibutor String
        Return Boolean - True if is the same name
    """
    inputNames = inputContributor.split(' ')
    actualNames = actualContibutor.split(' ')
    mainName = []
    for input in inputNames:
        for actual in actualNames:
            if (validateStringSimilarity(input, actual) > 0.9):
                mainName.append(actual)
                break
    if (contributorNameSimilarityIndex(len(inputNames), len(actualNames), len(mainName)) >= 0.5):
        return True
    return False  

def newContributors(contributorByWork, incomeContributors):
    """
    Function to compare two lists of contributors and create a new list with contributors that are not in the db 
    *@param contributorByWork List    
    *@param incomeContributors List
        Return List - New Contributors
    """
    prevContributors = [x.name for x in contributorByWork]
    newContributors = []
    for prevContributor in prevContributors:
        for contributor in incomeContributors:
            sameContributor = validateContributorsSimilarity(prevContributor,contributor)
            if ( sameContributor or contributor in newContributors or contributor in prevContributors):
                pass
            else:
                newContributors.append(contributor)
    return newContributors

def saveContributors(contributors, work):
    """
    Auxiliar Function to Save Contributors in DB
    *@param contributors List
    *@param work Object
        Return Boolean
    """
    for contributor in contributors:
        newContributor = Contributor(name=contributor, work=work)
        newContributor.save()
        return True




