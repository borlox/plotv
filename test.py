#!/usr/bin/env python
import sys

from ROOT import *
from plotv import plot_version

pv = plot_version("_plots.root")

h1 = TH1F("h1", "", 10, 0, 10)
for i in xrange(10):
	h1.SetBinContent(i+1, 11 - (i+1))

c1 = TCanvas("c1", "", 800, 600)
h1.Draw()
pv.save(c1)

pv.tag("yeah, a tag (-:")
pv.comment("with tags!")
pv.close()
