from bs4 import BeautifulSoup
from pathlib import Path
import requests
import asyncio
import os


class YuriUpdateChecker():

    def __init__(self):
        self.chapterLink = ""
        self.chapterName = ""

    def isYuriUpdated(self):   
        r = requests.get("https://dynasty-scans.com/chapters/added")
        soup = BeautifulSoup(r.text, features="html.parser")
        chapterPage = soup.find('a', class_='name')
        lastUpdatedChapter = soup.find('a', class_='name').text
        self.chapterLink = chapterPage.get('href')

        fileName = "LatestUpdateComparison.txt"
        comparisonFile = open(fileName, 'r')

        if comparisonFile.readline() != lastUpdatedChapter:
            
           comparisonFile.close()
           comparisonFile = open(fileName, 'w')
           comparisonFile.write(lastUpdatedChapter)
           comparisonFile.close()
           self.chapterName=lastUpdatedChapter
           return False

        return True

    def getChapterNameFromLink(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features = "html.parser")
        chapterName = soup.find('b').text
        self.chapterName = chapterName
        return chapterName
        
    def getChapterName(self):
        return self.chapterName

    def getChapterLink(self):
        return self.chapterLink

    def getYuriName(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        yuriName = soup.find('b').find('a')

        if yuriName is None:
            yuriName = soup.find('b')
       
        return yuriName.text
            

    def downloadChapter(self, directory, yuriName, chapterName, chapterLink):
        #Creates the links I'm using
        domainName = "https://dynasty-scans.com"
        imageLink = ""
        
        #Creates r and soup and opens the chapter
        r = requests.get(domainName + chapterLink)
        soup = BeautifulSoup(r.text, features="html.parser")

        #Stores the page numbers into pageTitles
        pagesList = soup.find_all('a', class_='page')
        pageTitles = []

        for i in range(len(pagesList)):
            pageTitles.append(pagesList[i].text)

        #This will now create a list of all the links to all the images in the chapter
        imageLinkList = []

        #This gets the image of the first page, which is needed for the first part of the link
        imageLink = soup.find('img', attrs={"alt": pageTitles[0]})
        imageLink = imageLink.get('src')
        #This SPLITS the link so I can insert the page numbers manually instead of going to every different chapter individually
        #This is also why I made a link of the page titles
        splitLink = imageLink.split(pageTitles[0])
        imageSplitLink = splitLink[0]
        imageType = splitLink[len(splitLink)-1]

        if len(splitLink) > 2:
            i = 1
            while i < len(splitLink)-1:
                imageSplitLink = imageSplitLink + pageTitles[0] + splitLink[i]
                i = i+1
                    
        #Finally, the loop will make a list of the links of each page.
        for i in range(len(pageTitles)):
            imageLinkList.append(domainName + imageSplitLink + pageTitles[i] + imageType)

        #This will make sure every file made has a valid name
        invalidChars = ['/', '\\', ':', '*', '?', '"', '|', '<', '>' ]
        tempYuriName = yuriName
        tempChapterName = chapterName
        for i in range(len(yuriName)):
            if yuriName[i] in invalidChars:
                tempYuriName = tempYuriName.replace(yuriName[i], '')
                
        for i in range(len(chapterName)):
            if chapterName[i] in invalidChars:
                tempChapterName = tempChapterName.replace(chapterName[i], '')

        yuriName = tempYuriName
        chapterName = tempChapterName
        
        #These next two if statements will create a directroy for the chapter if it doesn't exist
        if not os.path.exists(directory + yuriName.strip()):
            os.mkdir(directory + yuriName.strip())
            
        #This if makes it so it'll skip making a second folder if its a one chapter thing
        if not yuriName == chapterName:
            if not os.path.exists(directory + yuriName.strip() + '/' + chapterName.split(yuriName)[1].strip()):
                os.mkdir(directory + yuriName.strip() + '/' + chapterName.split(yuriName)[1].strip())

        #This creates the directory will the file is downloaded
        if yuriName == chapterName:
            path = directory + yuriName.strip() + '/'
        else:
            path = directory + yuriName.strip() + '/' + chapterName.split(yuriName)[1].strip() + '/'
            

        i = 0
        extIsRight = True
        startingImageType = imageType
        while i < len(imageLinkList):
            #This downloads the images to the directory
            fullPath = Path(path + pageTitles[i].strip() + imageType.strip())
    
            try:
                if not os.path.exists(fullPath):
                    #This grabs the image
                    r = requests.get(imageLinkList[i])

                    with open(fullPath, 'wb') as f:
                        f.write(r.content)

                    if os.path.getsize(fullPath) < 2000:
                        extIsRight = False
                        if imageType == '.png':
                            imageType = '.jpg'
                                
                        elif imageType == '.jpg':
                            imageType = '.webp'

                        elif imageType == '.webp':
                            imageType = '.png'

                        else:
                            imageType = ".png"

                        imageLinkList[i] = domainName + imageSplitLink + pageTitles[i] + imageType
                        os.remove(fullPath)

                    else:
                        extIsRight = True
                        imageType = startingImageType
                        
                    if extIsRight:
                            i = i+1
                else:
                    i = i+1

            except FileNotFoundError:
                print("Oops directory not found")
                i = i+1
                    

    def downloadFullYuri(self, directory, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        chapters = soup.find_all('a', class_='name')
        chapterLinks = []
        for i in range(len(chapters)):
            chapterLinks.append(chapters[i].get('href'))
            chapterLinks[i] = "https://dynasty-scans.com" + chapterLinks[i]

        for i in range(len(chapterLinks)):
           self.downloadChapter(directory, self.getYuriName(chapterLinks[i]), self.getChapterNameFromLink(chapterLinks[i]), chapterLinks[i].split("https://dynasty-scans.com")[1])
        
        return chapterLinks
