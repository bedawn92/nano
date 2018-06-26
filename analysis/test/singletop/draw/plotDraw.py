import ROOT, json, os, getopt, sys, time
import nano.analysis.CMS_lumi
from nano.analysis.histoHelper import *


def valToName(strVar): 
  return strVar.replace(".", "").replace("(", "").replace(")", "").replace(" ", "")


listRDRun = [
  "2016B", "2016C", "2016D", "2016E", "2016F", "2016G", "2016H", 
]

#datalumi =  35900 #35.9fb-1
datalumi =  33274 #33.3fb-1

strSigTitle = "t-channel"
nSigColor = 2

strPathDraw = "%s/src/nano/analysis/test/singletop/draw"%os.environ[ "CMSSW_BASE" ]
dicSetDef = json.load(open(os.path.join(strPathDraw, "listSet.json")))
datasets = json.load(open("%s/src/nano/nanoAOD/data/dataset/dataset.json" % os.environ['CMSSW_BASE']))

channel = 2 # 0 : all, 1 : el, 2 : mu, 3 : el + mu, (-) : anti
plotvar = "lep1.Pt()"
dolog = False

try:
  opts, args = getopt.getopt(sys.argv[2:],"dp:",["plotvar","dolog"])
except getopt.GetoptError:          
  print 'Usage : ./[name of the py file] [histogram directory] -p <plotvar> -d <dolog>'
  sys.exit(2)

for opt, arg in opts:
  if opt == '-h':
    print 'Usage : ./[name of the py file] [histogram directory] -p <plotvar> -d <dolog>'
    sys.exit()
  elif opt in ("-p", "--plotvar"):
    plotvar = arg
  elif opt in ("-d", "--dolog"):
    dolog = True

if plotvar not in dicSetDef[ "Vars" ].keys(): 
  print "This variable is not registered in listSet.json. Please add info about this variable."
  sys.exit(1)

binning = dicSetDef[ "Vars" ][ plotvar ][ "bin" ]
x_name  = dicSetDef[ "Vars" ][ plotvar ][ "xaxis" ]
y_name  = dicSetDef[ "Vars" ][ plotvar ][ "yaxis" ]

strDirHist = sys.argv[ 1 ].replace("/", "")

strVarName = valToName(plotvar)

dicSet= {}

dicSet[ "SingleTbar_t-channel" ] = {"TYPE": "SIG"}
dicSet[ "SingleTop_t-channel" ] = {"TYPE": "SIG"}
for strKey in dicSetDef[ "listDatasets" ][ "BKG" ]: dicSet[ strKey ] = {"TYPE": "BKG"}

if channel == 0 or ( abs(channel) & 1 ) != 0: 
  for strKey in dicSetDef[ "listDatasets" ][ "RDEL" ]: dicSet[ strKey ] = {"TYPE": "RD"}
if channel == 0 or ( abs(channel) & 2 ) != 0: 
  for strKey in dicSetDef[ "listDatasets" ][ "RDMU" ]: dicSet[ strKey ] = {"TYPE": "RD"}

for strKey in dicSet.keys():
  nTooMany = 1
  for strTooMany in dicSetDef[ "listDatasets" ][ "TooMany" ]: 
    if strTooMany in strKey: 
      nTooMany = 2
      break
  
  strNameRoot = "hist_" + strKey.encode("ascii", "ignore")
  strNameHist = strNameRoot + "_" + strVarName
  
  dicSet[ strKey ][ "hist" ] = ROOT.TH1F(strNameHist + "_new", strNameHist + "_new", 
    binning[ 0 ], binning[ 1 ], binning[ 2 ])
  dicSet[ strKey ][ "entries" ] = 0
  
  for nIdxTooMany in range(nTooMany): 
    strIdx = "" if nTooMany <= 1 else "%i"%( nIdxTooMany + 1 )
    strNameRootIdx = strNameRoot + strIdx
    strNameHistIdx = strNameRootIdx + "_" + strVarName
    
    fRoot = ROOT.TFile(os.path.join(strPathDraw, strDirHist, strNameRootIdx + ".root"))
    
    histLoad = fRoot.Get(strNameHistIdx)
    histLoad.Sumw2(False)
    
    dicSet[ strKey ][ "hist" ].Add(histLoad)
    dicSet[ strKey ][ "entries" ] += int(fRoot.Get("entries").GetTitle())
    
    fRoot.Close()

# Calculating the luminosity
#for strRun in listRDRun: 

listMCSig = []
listMC = []
histRD  = ROOT.TH1F("histRD",  "histRD",  binning[ 0 ], binning[ 1 ], binning[ 2 ])

# Inserting MC plots into stacks, merging RD plots, colouring, etc.
for strKey in dicSet.keys():
  dicSetInfo = findDataSet(strKey, datasets)
  
  # Scaling; the actual entry must be xsec * lumi ( * additional weight if there is)
  scale = 1.0
  if dicSet[ strKey ][ "TYPE" ] != "RD": 
    scale = datalumi * dicSetInfo[ "xsec" ] / dicSet[ strKey ][ "entries" ]
    if strKey in dicSetDef[ "Additional" ].keys(): 
      scale = scale * dicSetDef[ "Additional" ][ strKey ][ "AddWeight" ]
  
  if dicSet[ strKey ][ "TYPE" ] == "SIG": 
    dicSet[ strKey ][ "hist" ].Scale(scale)
    
    # Decoration; titling, colouring
    dicSet[ strKey ][ "hist" ].SetTitle(strSigTitle)
    dicSet[ strKey ][ "hist" ].SetFillColor(nSigColor)
    dicSet[ strKey ][ "hist" ].SetLineColor(nSigColor)
    
    # Appending
    listMCSig.append(dicSet[ strKey ][ "hist" ])
  elif dicSet[ strKey ][ "TYPE" ] == "BKG": 
    dicSet[ strKey ][ "hist" ].Scale(scale)
    
    # Loading cosmetric custom if there is
    strTitle = dicSetInfo[ "title" ]
    dicCustom = {} if strTitle not in dicSetDef[ "CosmetCustom" ] else dicSetDef[ "CosmetCustom" ][ strTitle ]
    
    # Decoration; more complicated than SIG because of custom
    strTitleR = dicSetInfo[ "title" ] if "title" not in dicCustom else dicCustom[ "title" ]
    nColor = dicSetInfo[ "colour" ] if "colour" not in dicCustom else dicCustom[ "colour" ]
    
    dicSet[ strKey ][ "hist" ].SetTitle(strTitleR)
    dicSet[ strKey ][ "hist" ].SetFillColor(nColor)
    dicSet[ strKey ][ "hist" ].SetLineColor(nColor)
    
    # Ordering (by title)!
    # Using a method giving an atttraction between samples with same title
    nIdx = 0
    for i in range(len(listMC)): 
      if listMC[ len(listMC) - 1 - i ].GetTitle() == dicSetInfo[ "title" ]: 
        nIdx = len(listMC) - 1 - i
        break
    
    listMC.insert(nIdx, dicSet[ strKey ][ "hist" ])
  elif dicSet[ strKey ][ "TYPE" ] == "RD": 
    # Well, no more than black dots for RD. Problem?
    histRD.Add(dicSet[ strKey ][ "hist" ])

# Send the following samples under ground (in the stack)
listBack = ["QCD", "t#bar{t}+Jets"]
for strBack in listBack: 
  for i in range(len(listMC)): 
    if strBack == listMC[ i ].GetTitle(): listMC.insert(0, listMC.pop(i))

if dolog: listMC.reverse()

# Signal part must be on the top
listMC += listMCSig

# Print it out!
canvMain = drawTH1("asdf", CMS_lumi, listMC, histRD, x_name, y_name, dolog)
canvMain.SaveAs("hist_%s_%s.png"%(strDirHist, strVarName))

