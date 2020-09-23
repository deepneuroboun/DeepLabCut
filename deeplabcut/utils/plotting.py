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
import numpy as np
import matplotlib.pyplot as plt
from plotnine import ggplot, geom_point, aes, geom_histogram
import os


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

def vec_p(x1, y1, x2, y2):
    return x1 * y2 - y1 * x2

def FieldPlots(tmpfolder, Dataframe, scorer, cfg, bodyparts2plot, options, suffix='.png'):
    FPS = 24.99
    plt.figure(figsize=(8,6))
    pcutoff = cfg['pcutoff']
    colors = get_cmap(len(bodyparts2plot),name = cfg['colormap'])
    alphavalue = cfg['alphavalue']

    # Vector based rectangular calculation
    vector_based = options['vector-based']
    for bpindex, bp in enumerate(bodyparts2plot):
        filtered_index = Dataframe[scorer][bp]['likelihood'].values > pcutoff
        filtered_dataframe = Dataframe[scorer][bp][filtered_index]
        # Keep this part until optimization
        xValues = Dataframe[scorer][bp]['x'].values[filtered_index]
        yValues = Dataframe[scorer][bp]['y'].values[filtered_index]
        bases = []
        region_cnt = len(vector_based['start'])
        for elem in zip(xValues, yValues):
            for i in range(region_cnt):
                fi_v_x, fi_v_y = vector_based['end'][i]
                fi_v_x = fi_v_x - vector_based['start'][i][0]
                fi_v_y = fi_v_y - vector_based['start'][i][1]

                t_v_x = elem[0] - vector_based['start'][i][0]
                t_v_y = elem[1] - vector_based['start'][i][1]

                fi_res = vec_p(fi_v_x, fi_v_y, t_v_x, t_v_y)

                se_v_x, se_v_y = vector_based['end'][(i+1) % region_cnt]
                se_v_x = se_v_x -  vector_based['start'][(i+1) % region_cnt][0]
                se_v_y = se_v_y - vector_based['start'][(i+1) % region_cnt][1]

                t_v_x = elem[0] - vector_based['start'][(i+1) % region_cnt][0]
                t_v_y = elem[1] - vector_based['start'][(i+1) % region_cnt][1]

                se_res = vec_p(se_v_x, se_v_y, t_v_x, t_v_y)

                if fi_res > 0 and se_res < 0:
                    bases.append(i+1)
                    break
        filtered_dataframe['bases'] = bases
        p = (ggplot(filtered_dataframe, aes(x='bases')) + geom_histogram())
        p.save(os.path.join(tmpfolder,"regions"+suffix), dpi=1000)
        break
    print("First Part Completed!")





def PlottingResults(tmpfolder,Dataframe,scorer,cfg, bodyparts2plot, showfigures, options, suffix='.png'):
    FieldPlots(tmpfolder, Dataframe, scorer, cfg, bodyparts2plot, options)
    ''' Plots poses vs time; pose x vs pose y; histogram of differences and likelihoods.'''
    plt.figure(figsize=(8, 6))
    pcutoff = cfg['pcutoff']
    colors = get_cmap(len(bodyparts2plot),name = cfg['colormap'])
    alphavalue = cfg['alphavalue']

    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot(Dataframe[scorer][bp]['x'].values[Index],Dataframe[scorer][bp]['y'].values[Index],'.',color=colors(bpindex),alpha=alphavalue)

    plt.gca().invert_yaxis()

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('X position in pixels')
    plt.ylabel('Y position in pixels')
    plt.savefig(os.path.join(tmpfolder,"trajectory"+suffix))
    plt.figure(figsize=(30, 10))
    Time=np.arange(np.size(Dataframe[scorer][bodyparts2plot[0]]['x'].values))

    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot(Time[Index],Dataframe[scorer][bp]['x'].values[Index],'--',color=colors(bpindex),alpha=alphavalue)
        plt.plot(Time[Index],Dataframe[scorer][bp]['y'].values[Index],'-',color=colors(bpindex),alpha=alphavalue)

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('Frame Index')
    plt.ylabel('X-(dashed) and Y- (solid) position in pixels')
    plt.savefig(os.path.join(tmpfolder,"plot"+suffix))

    plt.figure(figsize=(30, 10))
    for bpindex, bp in enumerate(bodyparts2plot):
        Index=Dataframe[scorer][bp]['likelihood'].values > pcutoff
        plt.plot(Time,Dataframe[scorer][bp]['likelihood'].values,'-',color=colors(bpindex),alpha=alphavalue)

    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap(cfg['colormap']), norm=plt.Normalize(vmin=0, vmax=len(bodyparts2plot)-1))
    sm._A = []
    cbar = plt.colorbar(sm,ticks=range(len(bodyparts2plot)))
    cbar.set_ticklabels(bodyparts2plot)
    plt.xlabel('Frame Index')
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
    >>> deeplabcut.plot_trajectories('home/alex/analysis/project/reaching-task/config.yaml',['/home/alex/analysis/project/videos/reachingvideo1.avi'])
    --------

    """
    cfg = auxiliaryfunctions.read_config(config)
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
        else:
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

    print('Plots created! Please check the directory "plot-poses" within the video directory')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('video')
    cli_args = parser.parse_args()
