"""
The plotv module/command for saving multiple versions of ROOT plots.


Module
======
Use the plot_version class from this module to save versioned plots.

>>> from plotv import plot_version
>>> pv = plot_version()

to use the default file name or use

>>> pv2 = plot_version("filename.root")

to specify a file name.

Then you create your ROOT plots and save them using

>>> pv.save(canvas)
>>> pv.save(canv2, "NewName")

You should add an comment using

>>> pv.comment("Fixed plot style issues")

If your version is special, you can tag it with a message

>>> pv.tag("This seems to be good!")

At the end, close the root file using

>>> pv.close()


Tool
====
You can use plotv as a tool to list plots in a versioned file and to get plots
of a specific version.

Use 
$ plotv.py --help
to display the help message.

"""
from datetime import datetime
from ROOT import *

class plot_version:
	@staticmethod
	def get_default_file():
		return "_plots.root"

	def __init__(self, file_name = ""):
		"""
		Initialize the plot_version object
		"""

		if file_name == "":
			file_name = plot_version.get_default_file()

		self.root_file = TFile(file_name, "update")

		now = datetime.now().replace(microsecond = 0)
		self.datestr = now.isoformat("_").replace(":","-")

		self.directory = self.root_file.Get(self.datestr)
		if not self.directory:
			self.directory = self.root_file.mkdir(self.datestr)

		self.tagged = False
		self.commented = False

	def close(self):
		"""
		Close the internal root file
		"""
		self.root_file.Close()

	def comment(self, comment):
		"""
		Save the comment to the root file
		"""
		obj = TNamed("comment", comment)
		self.directory.WriteTObject(obj)
		self.commented = True

	def tag(self, msg):
		obj = TNamed("tag", msg)
		self.directory.WriteTObject(obj)
		self.tagged = true

	def save(self, plot, name = ""):
		"""
		Save the plot to the root file
		"""
		if name == "":
			name = plot.GetName()
		self.directory.WriteTObject(plot, name)

#-------------------------------------------------------------------------------

import sys
import os
from getopt import getopt, GetoptError
from collections import namedtuple

get_cmd   = namedtuple("get_cmd", "type id")
list_cmd  = namedtuple("list_cmd", "type")

def load_content(rf):
	content = []
	for key in rf.GetListOfKeys():
		content.append(key.GetName())
	return content

def list_content(rf):
	content = load_content(rf)

	for i, key in enumerate(content):
		fdir = rf.Get(key)

		tag = fdir.Get("tag")

		comment = fdir.Get("comment")
		commentstr = ""
		if comment:
			commentstr = comment.GetTitle()

		print "%s %2d - %s - %s" % (tag and "*" or " ", i+1, key, commentstr)
		fdir = rf.Get(key)

		if tag:
			print "  Tag:", tag.GetTitle()

def get_outdir(outdir, key):
	if "{key}" in outdir:
		outdir = outdir.format(key = key)
	return outdir

def save_obj(obj, opt):
	prefix = opt['outdir'] + "/" + obj.GetName()

	for tp in opt['types']:
		obj.SaveAs(prefix + "." + tp)

def get_content(rf, cmd, opt):
	content = load_content(rf)

	if rf.Get(cmd.id):
		key = cmd.id
	else:
		idx = int(cmd.id)
		if idx <= 0 or idx > len(content):
			print "Error: Invalid id", cmd.id
		key = content[idx - 1]

	fdir = rf.Get(key)

	comment = fdir.Get("comment")

	print "Loading plots for %s" % key
	if comment:
		print "Comment:", comment.GetTitle()

	opt['outdir'] = get_outdir(opt['outdir'], key)

	if not os.path.exists(opt['outdir']):
		print "Creating output directory:", opt['outdir']
		os.makedirs(opt['outdir'])

	filter = ['comment', 'tag']
	for subkey in fdir.GetListOfKeys():
		if subkey.GetName() not in filter:
			obj = fdir.Get(subkey.GetName())
			save_obj(obj, opt)

#-------------------------------------------------------------------------------

def _defopts():
	return {
		'types': ["png"],
		'outdir': "{key}",
	}

def _usage(msg = False):
	if msg:
		print msg

	d = _defopts()

	print "Usage: %s <options> <command> [file]" % sys.argv[0]
	print "  Options:"
	print "    -h / --help        - Print this help message"
	print "    -t / --type <type> - Add output file type (default: %s)" % ", ".join(d['types'])
	print "    -o <directory>     - Output directory (default: %s)" % str(d['outdir'])
	print ""
	print "  Commands: "
	print "    list       - List the contents of the file"
	print "    get <id>   - Get all plots of <id>"
	print ""
	print "  File defaults to '%s'" % plot_version.get_default_file()

	sys.exit()

def _getopts():
	short_opts = "ht:o:"
	long_opts = ["help", "type="]

	options = _defopts()

	try:
		opts, args = getopt(sys.argv[1:], short_opts, long_opts)
	except GetoptError as err:
		_usage("Error: " + err.msg)

	for o, a in opts:
		if o == "-t" or o == "--type":
			if not a in options['types']:
				options['types'].append(a)
		elif o == "-o":
			options['outdir'] = a
		elif o == "-h" or o == "--help":
			usage()

	if len(args) < 1:
		_usage("Error: No command given")

	file_arg = 1
	if args[0] == "list":
		cmd = list_cmd("list")
	elif args[0] == "get":
		if len(args) < 2:
			_usage("Error: Not enough arguments for 'get'")
		cmd = get_cmd("get", args[1])
		file_arg = 2
	elif args[0] == "help":
		_usage()

	if len(args) < (file_arg+1):
		filename = plot_version.get_default_file()
	else:
		filename = args[file_arg]

	return cmd, options, filename

def _main():
	cmd, opt, fn = _getopts()

	root_file = TFile(fn, "open")

	if cmd.type == "list":
		list_content(root_file)
	elif cmd.type == "get":
		get_content(root_file, cmd, opt)

if __name__ == "__main__":
	_main()
