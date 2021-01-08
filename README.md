# Modified Version of DeepLabCut
This is a modified version of the pose estimation library [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut) ([Mathis et al, 2018](https://www.nature.com/articles/s41593-018-0209-y);[Nath, Mathis et al., 2019](https://www.nature.com/articles/s41596-019-0176-0)).

It includes a custom graphical user interface that makes it easy to define regions of interest and perform some commonly used analyses. 

## Pick a paradigm
![Image of Paradigms](https://github.com/deepneuroboun/DeepLabCut/blob/boun/images/Welcome.PNG)

## Select regions you want to analyse and generate plots easily
![Image of ROI](https://github.com/deepneuroboun/DeepLabCut/blob/boun/images/fast_demo.gif)
![Image of Custom ROI](https://github.com/deepneuroboun/DeepLabCut/blob/boun/images/fast_demo_custom.gif)


![Image of Quartile](https://github.com/deepneuroboun/DeepLabCut/blob/boun/images/quartile_plot_demo.png)

### Note:
- We did not include the models and the corresponding config files for the paradigms in the repository because they are too large. Please create a folder called paradigms under DeepLabCut and another folder inside paradigms called Free. Then place the config.yaml under DeepLabCut to the Free folder. This config file can serve as a template and help you try out the GUI (though model is not included). You are also welcome to try the other paradigms by making folders with the corresponding paradigm names, but the regions in those paradigms are hard-coded to specifically accomodate the camera positions in our experiments.

- This version lacks the standard GUI of DeepLabCut and is not up to date with the original repository. If you want to use this version, we recommend setting it up separately.

- It is a work in progress!