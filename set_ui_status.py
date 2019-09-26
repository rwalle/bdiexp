
def set_ui_status(ui, status_txt):

    #ctrl\":\"(\w+)\"
    #ctrl":ui.$1
    
    if status_txt in ['ctrl', 'disabled', 'enabledIP', 'enabledFP', 'preview', 'measuring']:
        status = [{"ctrl":ui.rdBtnIP,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.rdBtnFP,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.fpMinValTipLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.fpMinValLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.fpMaxValTipLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.fpMaxValLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.fpSatValTipLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.fpSatValLbl,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.showHologramChkbox,"disabled":0,"enabledIP":0,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.showFFTChkbox,"disabled":0,"enabledIP":0,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.showCroppedChkbox,"disabled":0,"enabledIP":0,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.useGPUChkbox,"disabled":0,"enabledIP":0,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.gaussBlurChkbox,"disabled":0,"enabledIP":0,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnStrt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnStop,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":1,"measuring":0},{"ctrl":ui.edtSaveFilename,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnSaveImg,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnMCN01,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnMCN003,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnMCP003,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnMCP01,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblCtrlSts,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":1},{"ctrl":ui.lblCtrlStsText,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":1},{"ctrl":ui.lblCtrlInf,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":1},{"ctrl":ui.lblCtrlInfText,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":1},{"ctrl":ui.lblCtrlSmplNo,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.ctrlSmpNospinBox,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.monitorOffChkbox,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnCtrlStrt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnCtrlHlt,"disabled":0,"enabledIP":0,"enabledFP":0,"preview":0,"measuring":1},{"ctrl":ui.lblCtrlStrtTime,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.lblCtrlStrtTimeTxt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.lblCtrlEndTime,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.lblCtrlEndTimeTxt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.btnEnableAll,"disabled":1,"enabledIP":0,"enabledFP":0,"preview":0,"measuring":0},{"ctrl":ui.btnDisableAll,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":0,"measuring":0},{"ctrl":ui.lblLamp,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnLmpOn,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnLmpOff,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblSLD,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblSLDHIOutput,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblSLDHIOutputTxt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblSLDPower,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.lblSLDPowerTxt,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnSLDChkSts,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnSLDSwtchHI,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnSLDSetHION,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0},{"ctrl":ui.btnSLDSwtchPower,"disabled":0,"enabledIP":1,"enabledFP":1,"preview":1,"measuring":0}]
        for cp in status:
            cp['ctrl'].setEnabled(cp[status_txt])


