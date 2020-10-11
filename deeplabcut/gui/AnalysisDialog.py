import wx
from pubsub import pub




class AnalysisDialog(wx.ProgressDialog):
    def __init__(self):
        super().__init__("Video Analysis Progress",
                "Current Video Name should be shown here",
                style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE)
        pub.subscribe(self.listener, "analyze_listener")

    def listener(self, curValue):
        print("Is it???")
        self.Update(curValue)
        if (curValue > self.GetRange()):
            self.Destroy()



