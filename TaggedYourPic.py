import Tkinter, Tkconstants, tkFileDialog
import os
from shutil import copyfile
from clarifai.client import ClarifaiApi
clarifai_api = ClarifaiApi()
clarifai_api.CLIENT_ID = 'su3n1HOTBFHOA-pB_RzC9jH0frBMO70-whHo2smX'
clarifai_api.access_token = 'FFQGf04WcDuZx5Ec3JOuYgPpLM6JUT'

class TaggedYourPic(Tkinter.Frame):
  
  def __init__(self, root):

    global listbox
    global AllTagList
    
    Tkinter.Frame.__init__(self, root)

    # define buttons
    OpenFolder = Tkinter.Button(self, text='Open Picture Folder', command=self.openfolder)
    OpenFolder.grid(row=0)
    Tkinter.Button(self, text='Save Pictures to Folders', command=self.savefolder).grid(row=3)
    #Tkinter.Button(self, text='Clear List', command=self.clear).grid(row=4)

    frame = Tkinter.Frame(root)
    frame.grid(row = 1)
    labels = Tkinter.Text(frame, height = 1, width = 32)
    labels.pack(side="top",fill="x")
    labels.insert("end","Tag \t\t Number of Photos")
    scrollbar = Tkinter.Scrollbar(frame)
    listbox = Tkinter.Listbox(frame, width = 32, height = 18, selectmode = "multiple", yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side='right', fill='y')
    listbox.pack(side='left', fill='both', expand=1)
    
    # define options for opening or saving a file
    self.file_opt = optionsFile = {}
    optionsFile['defaultextension'] = '.txt'
    #optionsFile['filetypes'] = [('all files', '.*'), ('text files', '.jpg')]
    optionsFile['initialdir'] = 'C:\\'
    optionsFile['initialfile'] = 'myfile.txt'
    optionsFile['parent'] = root
    optionsFile['title'] = 'This is a title'

    # defining options for opening a directory
    self.dir_opt = options = {}
    options['initialdir'] = 'C:\\'
    options['mustexist'] = False
    options['parent'] = root
    options['title'] = 'This is a title'

  def savefolder(self):
    self.newfolderpath = (tkFileDialog.askdirectory(**self.dir_opt))
    selected = listbox.curselection()
    selectedList = []
    for i in range(len(selected)):
      item = listbox.get(selected[i]).split(' ')
      selectedList.append(item[0])

    usedphotos = []
    PhotoDict = {}
    PhotoDictionary = {}
    for x in range(len(self.AllTagList)):
      Photoindexlist = []
      for item in self.AllTagList[x]:
        if item in selectedList:
          Photoindexlist.append(self.AllTagList[x].index(item))
          if self.photolist[x] not in usedphotos:
            usedphotos.append(self.photolist[x])
          PhotoDict[self.photolist[x]] = [min(Photoindexlist), x]
          
    for tag in selectedList:
      PhotoDictionary[tag] = []
    PhotoDictionary["Other"] = []

    for photo in self.photolist:
      if photo in PhotoDict:
        PhotoDictionary[self.AllTagList[self.photolist.index(photo)][PhotoDict[photo][0]]].append(photo)
      else:
        PhotoDictionary["Other"].append(photo)
    
    for tag in PhotoDictionary:
      os.mkdir(self.newfolderpath+"/"+tag)
      for photo in PhotoDictionary[tag]:
        copyfile(self.folderpath+"/"+photo, self.newfolderpath+"/"+tag+"/"+photo)
    print("Done")

  def openfolder(self):
    def fillListBox(listbox, wordList):
      for i in wordList:
        spaces = ""
        n = 35-len(i[0])
        for s in range(n):
          spaces += " "
        listbox.insert('end', i[0] + spaces + "\t" + str(i[1]))
        
    self.folderpath = (tkFileDialog.askdirectory(**self.dir_opt))

    WordDictionary = {} #big dictionary that carries words with counters

    for subdir, dirs, files in os.walk(self.folderpath):
      for f in files:
        self.photolist.append(f)
        result = clarifai_api.tag_images(open(self.folderpath+"/"+f, 'rb'))
        wordlist = result[u'results'][0][u'result'][u'tag'][u'classes'] #word tags list
        #problist = result[u'results'][0][u'result'][u'tag'][u'probs'] #probability tags list
        TagProbList = [] #list that will hold both for each respective photo
        for x in range(len(wordlist)): 
            if str(wordlist[x]) not in TagProbList: #make sure the same word from the photo list does not get in
                TagProbList.append(str(wordlist[x]))#words with their tuples put into a list
                if str(wordlist[x]) not in WordDictionary.keys():
                    WordDictionary[str(wordlist[x])] = 1
                else:
                    WordDictionary[str(wordlist[x])]+= 1
        self.AllTagList.append(TagProbList) #put it into the big list

    for x in WordDictionary.keys():
        if ((WordDictionary[x] >= (len(self.photolist) * 0.9)) or (WordDictionary[x] <= (len(self.photolist) * 0.11))):
            WordDictionary.pop(x)

    SortedItems = ['']*len(WordDictionary)
    for item in WordDictionary:
        for listIndex in range(len(SortedItems)):
            if [item, WordDictionary[item]] not in SortedItems:
                if SortedItems[0] == "":
                    SortedItems[0] = [item, WordDictionary[item]]
                elif SortedItems[listIndex] == '':
                    SortedItems[listIndex] = [item, WordDictionary[item]]
                elif WordDictionary[item] > SortedItems[listIndex][1]:
                    for backwardsIndex in range(len(SortedItems)-2,listIndex-1,-1):
                        SortedItems[backwardsIndex+1] = SortedItems[backwardsIndex]
                    SortedItems[listIndex] = [item, WordDictionary[item]]

    fillListBox(listbox, SortedItems)


if __name__=='__main__':
  root = Tkinter.Tk()
  root.resizable(width=True, height=True)
  root.geometry('{}x{}'.format(306, 395))
  TaggedYourPic.folderpath = ''
  TaggedYourPic.newfolderpath = ''
  TaggedYourPic.AllTagList = []
  TaggedYourPic.photolist = []
  TaggedYourPic(root).grid()
  root.mainloop()
