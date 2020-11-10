"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

####################################################
# Dependencies
####################################################
import os.path
from pathlib import Path
import argparse
from deeplabcut.utils import auxiliaryfunctions
from deeplabcut.pose_estimation_tensorflow import analyze_videos
import numpy as np
import matplotlib.pyplot as plt
from plotnine import ggplot, geom_point, aes, geom_histogram, labels
import os
import pandas as pd

# TODO: change hard coded FPS
FPS=24.99

# https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def Histogram(vector,color,bins):
    dvector=np.diff(vector)
    dvector=dvector[np.isfinite(dvector)]
    plt.hist(dvector,color=color,histtype='step',bins=bins)
#    fig.colorbar(im, ax=ax)

def vec_p(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    return x1 * y2 - y1 * x2


def in_region(region, target):
    vec_size = len(region)
    tx, ty = target
    for i in range(vec_size):
        start_x, start_y = region[i]
        end_x, end_y = region[(i+1) % vec_size]
        v1 = (end_x - start_x, end_y - start_y)
        v2 = (tx - start_x, ty - start_y)
        if vec_p(v1, v2) < 0:
            return False
    return True

def cm_pix_ratio(cfg):
    height = cfg['height']
    width = cfg['width']
    x1= cfg['x1']
    x2= cfg['x2']
    y1= cfg['y1']
    y2= cfg['y2']
    height_ratio= height/(y2-y1)
    width_ratio = width/(x2-x1)
    return height_ratio,width_ratio


def FieldPlots(tmpfolder, Dataframe, scorer, cfg, bodyparts2plot, options, suffix='.png'):
    plt.figure(figsize=(8,6))
    pcutoff = cfg['pcutoff']
    colors = get_cmap(len(bodyparts2plot),name = cfg['colormap'])
    alphavalue = cfg['alphavalue']


    bases_quartile = pd.DataFrame(np.zeros((len(Dataframe),len(bodyparts2plot))),columns = bodyparts2plot)
    bases_center = bases_quartile
    for bp in (bodyparts2plot):
        filtered_index = Dataframe[scorer][bp]['likelihood'].values > pcutoff
        filtered_dataframe = Dataframe[scorer][bp][filtered_index]
        # Keep this part until optimization
        xValues = Dataframe[scorer][bp]['x'].values[filtered_index]
        yValues = Dataframe[scorer][bp]['y'].values[filtered_index]
        for analysis in options.keys():
            cur_row = 0
            for elem in zip(xValues, yValues):
                index = -1
                for region in options[analysis].keys():
                    if (in_region(options[analysis][region], elem)):
                        if analysis == 'vector-based':
                            bases_quartile.loc[cur_row,bp] = region
                        else:
                            bases_center.loc[cur_row,bp] = region
                        index = region
                # TODO: needs some adjustments for inside-outside of regions
                if index == -1:
                    bases_center.loc[cur_row,bp] = 'peripheral'
                cur_row += 1
    
    to_plot = [[],[]]
    all_ROI = [bases_quartile,bases_center]
    plt_names = ["quartile","central"]
    for each in all_ROI:
        for row in range(len(each)):
            to_add = each.iloc[row].mode()[0]
            to_plot[all_ROI.index(each)].append(to_add)
        each["plot count"] = to_plot[all_ROI.index(each)]
        p = (ggplot(each, aes(x='plot count', y='stat(count/FPS)'))  + geom_histogram(binwidth=.5) +
            labels.labs(title = "Time Spent in Each Region",
            x="Region",
            y="Seconds")
            )
        p.save(os.path.join(tmpfolder,"regions-"+plt_names[all_ROI.index(each)]+suffix), dpi=1000)





def PlottingResults(tmpfolder,Dataframe,scorer,cfg, bodyparts2plot, showfigures, options, suffix='.png'):
    FieldPlots(tmpfolder, Dataframe, scorer, cfg, bodyparts2plot, options)
    ''' Plots poses vs time; pose x vs pose y; histogram of differences and likelihoods.'''
    plt.figure(figsize=(8, 6))
    pcutoff = cfg['pcutoff']
    colors = get_cmap(len(bodyparts2plot),name = cfg['colormap'])
    alphavalue = cfg['alphavalue']
    height_ratio,width_ratio = cm_pix_ratio(cfg)


    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot((Dataframe[scorer][bp]['x'].values[Index])*width_ratio,(Dataframe[scorer][bp]['y'].values[Index])*height_ratio,'.',color=colors(bpindex),alpha=alphavalue)

    plt.gca().invert_yaxis()

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('X position in centimeters')
    plt.ylabel('Y position in centimeters')
    plt.savefig(os.path.join(tmpfolder,"trajectory"+suffix))
    plt.figure(figsize=(30, 10))
    Time=(np.arange(np.size(Dataframe[scorer][bodyparts2plot[0]]['x'].values)))/FPS

    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot(Time[Index],(Dataframe[scorer][bp]['x'].values[Index])*width_ratio,'--',color=colors(bpindex),alpha=alphavalue)
        plt.plot(Time[Index],(Dataframe[scorer][bp]['y'].values[Index])*height_ratio,'-',color=colors(bpindex),alpha=alphavalue)

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('Seconds')
    plt.ylabel('X-(dashed) and Y- (solid) position in centimeters')
    plt.savefig(os.path.join(tmpfolder,"plot"+suffix))

    plt.figure(figsize=(30, 10))
    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot(Time,Dataframe[scorer][bp]['likelihood'].values,'-',color=colors(bpindex),alpha=alphavalue)

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('Seconds')
    plt.ylabel('Likelihood')

    plt.savefig(os.path.join(tmpfolder,"plot-likelihood"+suffix))

    plt.figure()
    bins=np.linspace(0,np.amax(Dataframe.max()),100)

    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values < pcutoff
        X=Dataframe[scorer][bp]['x'].values
        X[Index]=np.nan
        Histogram(X,colors(bpindex),bins)
        Y=Dataframe[scorer][bp]['x'].values
        Y[Index]=np.nan
        Histogram(Y,colors(bpindex),bins)

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.ylabel('Count')
    plt.xlabel('DeltaX and DeltaY')
    plt.savefig(os.path.join(tmpfolder,"hist"+suffix))

    if showfigures!=True:
        plt.close("all")
    else:
        plt.show()

##################################################
# Looping analysis over video
##################################################

def plot_trajectories(config, videos, options, videotype='.avi', shuffle=1, trainingsetindex=0, filtered=False,
                      displayedbodyparts='all', showfigures=False, destfolder=None):
    """
    Plots the trajectories of various bodyparts across the video.

    Parameters
    ----------
     config : string
    Full path of the config.yaml file as a string.

    videos : list
        A list of strings containing the full paths to videos for analysis or a path to the directory, where all the videos with same extension are stored.

    videotype: string, optional
        Checks for the extension of the video in case the input to the video is a directory.\n Only videos with this extension are analyzed. The default is ``.avi``

    shuffle: list, optional
    List of integers specifying the shuffle indices of the training dataset. The default is [1]

    trainingsetindex: int, optional
    Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).

    filtered: bool, default false
    Boolean variable indicating if filtered output should be plotted rather than frame-by-frame predictions. Filtered version can be calculated with deeplabcut.filterpredictions

    displayedbodyparts: list of strings, optional
        This select the body parts that are plotted in the video.
        Either ``all``, then all body parts from config.yaml are used,
        or a list of strings that are a subset of the full list.
        E.g. ['hand','Joystick'] for the demo Reaching-Mackenzie-2018-08-30/config.yaml to select only these two body parts.

    showfigures: bool, default false
    If true then plots are also displayed.

    destfolder: string, optional
        Specifies the destination folder that was used for storing analysis data (default is the path of the video).

    Example
    --------
    for labeling the frames
    >>> deeplabcut.plot_trajectories('~/analysis/project/reaching-task/config.yaml',['~/analysis/project/videos/reachingvideo1.avi'])
    --------

    """
    cfg = auxiliaryfunctions.read_config(config, is_paradigm=True)
    trainFraction = cfg['TrainingFraction'][trainingsetindex]
    DLCscorer,DLCscorerlegacy = auxiliaryfunctions.GetScorerName(cfg,shuffle,trainFraction) #automatically loads corresponding model (even training iteration based on snapshot index)
    bodyparts = auxiliaryfunctions.IntersectionofBodyPartsandOnesGivenbyUser(cfg, displayedbodyparts)
    Videos=auxiliaryfunctions.Getlistofvideos(videos,videotype)
    for video in Videos:
        print(video)
        if destfolder is None:
            videofolder = str(Path(video).parents[0])
        else:
            videofolder=destfolder

        vname = str(Path(video).stem)
        print("Starting % ", videofolder, video)
        notanalyzed, dataname, DLCscorer=auxiliaryfunctions.CheckifNotAnalyzed(videofolder,vname,DLCscorer,DLCscorerlegacy,flag='checking')

        if notanalyzed:
            print("The video was not analyzed with this scorer:", DLCscorer)
            analyze_videos(config, [video], videotype='.MP4')
        #LoadData
        print("Loading ", video, "and data.")
        datafound,metadata,Dataframe,DLCscorer,suffix=auxiliaryfunctions.LoadAnalyzedData(str(videofolder),vname,DLCscorer,filtered) #returns boolean variable if data was found and metadata + pandas array
        if datafound:
            basefolder=videofolder
            auxiliaryfunctions.attempttomakefolder(basefolder)
            auxiliaryfunctions.attempttomakefolder(os.path.join(basefolder,'plot-poses'))
            tmpfolder = os.path.join(basefolder,'plot-poses', vname)
            auxiliaryfunctions.attempttomakefolder(tmpfolder)
            PlottingResults(tmpfolder, Dataframe, DLCscorer, cfg, bodyparts, showfigures, options, suffix+'.png')
    return 'Plots created! Please check the directory "plot-poses" within the video directory'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('video')
    cli_args = parser.parse_args()
