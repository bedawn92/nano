#ifndef topObjectSelection_H
#define topObjectSelection_H

#include "nanoBase.h"
#include "nano/external/interface/TopTriggerSF.h"
//#include "nano/external/interface/TTbarModeDefs.h"

class topObjectSelection : public nanoBase
{
protected:
  std::vector<Float_t> b_csvweights;
  float b_btagweight, b_btagweight_up, b_btagweight_dn;
  Float_t b_isolep;
  
  Float_t b_maxBDiscr_nonb;
  
public:
  // YOU MUST SET UP ALL IN THE BELOW!!!
  // (SetCutValues() will force you to do it)
  Float_t cut_ElectronPt;
  Float_t cut_ElectronEta;
  Int_t  *cut_ElectronIDType; // For example, cut_ElectronIDType = Electron_cutBased;
  Int_t   cut_ElectronIDCut;
  Float_t cut_ElectronSCEtaLower;
  Float_t cut_ElectronSCEtaUpper;
  Float_t cut_ElectronRelIso03All;
  
  Bool_t *cut_MuonIDType; // For example, cut_MuonIDType = Muon_tightId;
  Float_t cut_MuonPt;
  Float_t cut_MuonEta;
  Float_t cut_MuonRelIso04All;
  
  Float_t cut_VetoElectronPt;
  Float_t cut_VetoElectronEta;
  Int_t  *cut_VetoElectronIDType; // For example, cut_VetoElectronIDType = Electron_cutBased;
  Int_t   cut_VetoElectronIDCut;
  Float_t cut_VetoElectronSCEtaLower;
  Float_t cut_VetoElectronSCEtaUpper;
  Float_t cut_VetoElectronRelIso03All;
  
  Bool_t *cut_VetoMuonIDType; // For example, cut_MuonIDType = NULL; or cut_MuonIDType = Muon_looseId;
  Float_t cut_VetoMuonPt;
  Float_t cut_VetoMuonEta;
  Float_t cut_VetoMuonRelIso04All;
  
  Float_t cut_GenJetPt;
  Float_t cut_GenJetEta;
  Float_t cut_GenJetConeSizeOverlap;
  
  Int_t   cut_JetID;
  Float_t cut_JetPt;
  Float_t cut_JetEta;
  Float_t cut_JetConeSizeOverlap;
  
  Int_t    cut_BJetID;
  Float_t  cut_BJetPt;
  Float_t  cut_BJetEta;
  Float_t  cut_BJetConeSizeOverlap;
  Float_t *cut_BJetTypeBTag; // For example, set it as cut_BJetTypeBTag = Jet_btagCSVV2;
  Float_t  cut_BJetBTagCut;

public: 
  // Tip: If you want to use your own additional cut with the existing cut, 
  // instead of copying the existing code, use the following: 
  // bool [YOUR CLASS NAME]::additionalConditionFor[...]() {
  //   if ( !topObjectSelection::additionalConditionFor[...]() ) return false;
  //   [YOUR OWN CONDITIONS...]
  // }
  virtual bool additionalConditionForElectron(UInt_t nIdx) {return true;};
  virtual bool additionalConditionForMuon(UInt_t nIdx) {return Muon_isPFcand[ nIdx ] && Muon_globalMu[ nIdx ];};
  virtual bool additionalConditionForVetoElectron(UInt_t nIdx) {return true;};
  virtual bool additionalConditionForVetoMuon(UInt_t nIdx) {
    return Muon_isPFcand[ nIdx ] && ( Muon_globalMu[ nIdx ] || Muon_trackerMu[ nIdx ] );
  };
  virtual bool additionalConditionForGenJet(UInt_t nIdx) {return true;};
  virtual bool additionalConditionForJet(UInt_t nIdx) {return true;};
  virtual bool additionalConditionForBJet(UInt_t nIdx) {return true;};
  
public:
  std::vector<TParticle> muonSelection();
  std::vector<TParticle> elecSelection();
  std::vector<TParticle> vetoMuonSelection();
  std::vector<TParticle> vetoElecSelection();
  std::vector<TLorentzVector> recoleps;
  //std::vector<TParticle> jetSelection(std::vector<Float_t> *csvVal = NULL);
  std::vector<TParticle> jetSelection();
  std::vector<TParticle> bjetSelection();

  std::vector<TParticle> genJetSelection();

  topObjectSelection(TTree *tree=0, TTree *had=0, TTree *hadTruth=0, Bool_t isMC = false);
  topObjectSelection(TTree *tree=0, Bool_t isMC=false) : topObjectSelection(tree, 0, 0, isMC) {}
  ~topObjectSelection() {}
  
  // In this function you need to set all the cut conditions in the above
  // If you do not set this function up (so that you didn't set the cuts), the compiler will deny your code, 
  // so you can be noticed that you forgot the setting up.
  // And you don't need to run this function indivisually; it will be run in the creator of this class.
  virtual int SetCutValues() = 0;
};

#endif
