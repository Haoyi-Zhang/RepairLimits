"""Draw the observation-timing witness directly as a font-embedded vector PDF."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

def draw(out):
    plt.rcParams.update({"font.family":"STIXGeneral","mathtext.fontset":"stix",
                         "font.size":8,"pdf.fonttype":42,"ps.fonttype":42,
                         "text.usetex":False,"axes.unicode_minus":False})
    fig=plt.figure(figsize=(3.35,1.85))
    ax=fig.add_axes([0,0,1,1],xlim=(0,8.5),ylim=(0,4.7));ax.axis("off")
    nodes={"prefix":(4.25,4.05,2.6,.55,r"shared prefix $a$"),
           "observe":(4.25,2.95,2.1,.55,r"observe $o$"),
           "left":(1.7,1.15,2.5,.55,r"tail of $r^0$"),
           "right":(6.8,1.15,2.5,.55,r"tail of $r^1$")}
    labels=[]
    for name,(x,y,w,h,text) in nodes.items():
        ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,edgecolor="black",
                               facecolor="white",linewidth=.6))
        labels.append(ax.text(x,y,text,ha="center",va="center"))
    def arrow(start,end):
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=7,
                                    linewidth=.6,color="black",shrinkA=0,shrinkB=0))
    arrow((4.25,3.775),(4.25,3.225))
    ax.plot([4.25,4.25],[2.675,2.1],color="black",lw=.6)
    ax.plot([1.7,6.8],[2.1,2.1],color="black",lw=.6)
    arrow((1.7,2.1),(1.7,1.425));arrow((6.8,2.1),(6.8,1.425))
    labels.append(ax.text(1.7,2.38,r"$o\ne D_i(r^0)$",ha="center",va="center"))
    labels.append(ax.text(6.8,2.38,r"$o=D_i(r^0)$",ha="center",va="center"))
    labels.append(ax.text(4.25,.28,r"$D_i(r^0)\ne D_i(r^1);\quad r^0_{<i}=r^1_{<i}=a$",
                          ha="center",va="center"))
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    for text in labels:
        bounds=text.get_window_extent(renderer).transformed(ax.transData.inverted())
        if bounds.x0<0 or bounds.x1>8.5 or bounds.y0<0 or bounds.y1>4.7:
            raise ValueError("clipped witness label: "+text.get_text())
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/"timing.pdf",metadata={"Creator":"Python Matplotlib",
                "Producer":None,"CreationDate":None,"ModDate":None})
    plt.close(fig)
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir",type=Path,default=Path(__file__).resolve().parent)
    draw(ap.parse_args().outdir)
