import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Arc
import os


circle_segments=12
figure_directory = 'figures/twelve_segments'

def create_axes(xlim,ylim):
    fig,ax = plt.subplots(figsize=(2*np.diff(xlim)[0],2*np.diff(ylim)[0]))

    # Setup Axes
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    plt.arrow(0,0,xlim[1]-.5,0,width=.02,fc='gray')
    plt.arrow(0,0,xlim[0]+.5,0,width=.02,fc='gray')
    plt.arrow(0,0,0,ylim[1]-.5,width=.02,fc='gray')
    plt.arrow(0,0,0,ylim[0]+.5,width=.02,fc='gray')

    # Eliminate upper and right axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Show ticks on the left and lower axes only
    ax.xaxis.set_tick_params(bottom='on', top='off',labelsize=28)
    ax.yaxis.set_tick_params(left='on', right='off',labelsize=28)

    # Move remaining spines to the center
    ax.spines['bottom'].set_position('zero') # spine for xaxis 
    #    - will pass through the center of the y-values (which is 0)
    ax.spines['left'].set_position('zero')  # spine for yaxis 
    #    - will pass through the center of the x-values (which is 5)

    plt.text(xlim[1]-.75,.25,"x",fontsize=28)
    plt.text(.25,ylim[1]-.5,"y",fontsize=28)

    return fig,ax


def calc_chord_length(radius,angle):
    return radius*2*np.sin(angle/2)



fig,ax = create_axes((-2,4),(-1,2))
ax.set_xticks([-1,1,2,3])
ax.set_yticks([])

# Add circle
ccenter = (0,.5)
ccol = 'blue'
clw = 6
circle = Arc(ccenter,1,1,edgecolor=ccol,linewidth=clw)
ax.add_patch(circle)


plt.savefig(os.path.join(figure_directory,'fig1.png'))

#%%

'''Roll circle to the right so that we create a new intersection which is 1/6
of the way along the circles circumference'''

segment_angle_deg = 360/circle_segments
segment_angle_rad = 2*np.pi/circle_segments



chord_length = calc_chord_length(.5,segment_angle_rad)

newcenter = (.5*chord_length,.5*np.cos(segment_angle_rad/2))
circle.center = newcenter[0],newcenter[1]

line = ax.plot([0,chord_length],[0,0],'.',color='yellow',markersize=15)[0]
fig.savefig(os.path.join(figure_directory,'fig2.png'))
#%%

# Roll the circle to the right, each time leaving an arc on the x-axis and 
# removing the arc from the circle.  Repeat until circle is all used up.

circle.theta1=270-segment_angle_deg/2
circle.theta2 = circle.theta1

for k in range(0,circle_segments-1):
    arc = Arc(newcenter,1,1,0,270-segment_angle_deg/2,270+segment_angle_deg/2,lw=clw,edgecolor=ccol)
    ax.add_patch(arc)
    newcenter = (newcenter[0]+chord_length,newcenter[1])
    circle.theta2=circle.theta2-segment_angle_deg
    circle.center = newcenter
    xmarkers = np.append(line.get_xdata(),line.get_xdata()[-1]+chord_length)
    line.set_data(xmarkers,np.zeros(len(xmarkers)))
    fig.savefig(os.path.join(figure_directory,'fig{}.png'.format(3+k)))

chordsum = circle_segments*chord_length  
chordstr = str(chordsum)

from decimal import Decimal

d = Decimal(chordsum)
digits = d.as_tuple().digits
if len(digits)>6:
    anntext = str(digits[0]) + '.' + ''.join([str(x) for x in digits[1:6]]) + '...'
else:
    anntext = str(chordsum)
    
annotation = ax.annotate(anntext,xy=(chordsum,0),xytext=(chordsum,.75),ha='center',
            fontsize=24,arrowprops=dict(arrowstyle="->"))  

fig.savefig(os.path.join(figure_directory,'final.png'))

#%%
# Plot of chord length with circle segments
    
nsg = [2,3,4,6,12,36]
chordlen = [chord_length(.5,2*np.pi/n) for n in nsg]

plt.plot(nsg,chordlen,'.',nsg,chordlen*np.array(nsg),'.')

plt.plot([0,36],[np.pi,np.pi],linestyle='--',color='black')




#%%
# Measure sqrt 2
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

figure_directory = 'figures/measure_sqrt2'
fig,ax = create_axes((-1,3),(-1,2))
square = Rectangle((0,0),1,1,fill=False,linewidth=7,edgecolor='blue')
ax.add_patch(square)

line = ax.plot([0,0,1,1],[0,1,0,1],'.',color='yellow',markersize=15)[0]

a1 = ax.annotate('',xy=(0,0),xytext=(.6,.6),arrowprops=dict(arrowstyle="->"),fontsize=24)
b1 = ax.annotate('',xy=(1,1),xytext=(.5,.5),arrowprops=dict(arrowstyle="->"),fontsize=24)
c1 = ax.text(.2,.55,r'$\sqrt{2}$',fontsize=24)


a2 = ax.annotate('',xy=(0,-.1),xytext=(.6,-.1),arrowprops=dict(arrowstyle="->"),fontsize=24)
b2 = ax.annotate('',xy=(1,-.1),xytext=(.5,-.1),arrowprops=dict(arrowstyle="->"),fontsize=24)
c2 = ax.text(.5,-.3,'1',fontsize=24)


a3 = ax.annotate('',xy=(1.1,0),xytext=(1.1,.6),arrowprops=dict(arrowstyle="->"),fontsize=24)
b3 = ax.annotate('',xy=(1.1,1),xytext=(1.1,.5),arrowprops=dict(arrowstyle="->"),fontsize=24)
c3 = ax.text(1.3,.5,'1',fontsize=24)

ax.set_xticks([])
ax.set_yticks([])
fig.savefig(os.path.join(figure_directory,'fig0.png'))
#arc = Arc((0,0),2*np.sqrt(2),2*np.sqrt(2),0,0,45,linestyle='--')
#ax.add_patch(arc)

#plt.arrow(np.sqrt(2),-.5,0,.5,width=.02,fc='gray')


#%%
ax.set_xticks([1,2])
ax.set_yticks([1])
a1.set_visible(False)
b1.set_visible(False)
c1.set_visible(False)
a2.set_visible(False)
b2.set_visible(False)
c2.set_visible(False)
a3.set_visible(False)
b3.set_visible(False)
c3.set_visible(False)
fig.savefie(os.path.join(figure_directory,'fig1.png'))

#%%
trans_data = Affine2D().rotate_deg(-15) + ax.transData
square.set_transform(trans_data)
line.set_transform(trans_data)
fig.savefig(os.path.join(figure_directory,'fig2.png'))
#%%
trans_data = Affine2D().rotate_deg(-30) + ax.transData
square.set_transform(trans_data)
line.set_transform(trans_data)

fig.savefig(os.path.join(figure_directory,'fig3.png'))

#%%

trans_data = Affine2D().rotate_deg(-45) + ax.transData
square.set_transform(trans_data)
line.set_transform(trans_data)

ax.annotate(r'$\sqrt{2}$',xy=(np.sqrt(2),0),xytext=(np.sqrt(2),-.75),ha='center',
            fontsize=24,arrowprops=dict(arrowstyle="->"))

fig.savefig(os.path.join(figure_directory,'fig4.png'))