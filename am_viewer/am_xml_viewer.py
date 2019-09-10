"""
 AM Viewer
 Copyright (c) 2019, Dolby Laboratories Inc.
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without modification, are permitted
 provided that the following conditions are met:
 
 1. Redistributions of source code must retain the above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
    and the following disclaimer in the documentation and/or other materials provided with the distribution.
 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
    promote products derived from this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
 WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD

try:
    from ttk import Treeview, Scrollbar, Frame
    from Tkconstants import HORIZONTAL, VERTICAL, N,S,E,W, END
except ImportError:
    from tkinter.ttk import Treeview, Scrollbar, Frame
    from tkinter.constants import HORIZONTAL, VERTICAL, N,S,E,W, END
    
import xml.etree.ElementTree as ET

from operator import attrgetter


# The following two function should be contributed back to the pmd and adm modules
# For now they are being used here
# these functions allow either a PMD or SADM xml file to be analyzed from the command line

def isFilePmd(fileHandle):
    tree = ET.ElementTree(file=fileHandle)
    tree.getroot()
    root = tree.getroot()
    pmd_root = root.find(PMD_XML_ROOT_SE_PMD)
    fileHandle.seek(0) # rewind file so that it can still be parsed
    if pmd_root == None:
        return(False)
    else:
        return(True)

def isFileSADM(fileHandle):
    tree = ET.ElementTree(file=fileHandle)
    tree.getroot()
    root = tree.getroot()
    sadm_format_root = root.find('coreMetadata')
    fileHandle.seek(0) # rewind file so that it can still be parsed
    if sadm_format_root == None:
        return(False)
    else:
        return(True)





# Parameters
# 1. Interface
# 2. Multicast IP address

def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)

class XML_Viewer(Frame):

    def __init__(self, master, xml=None, heading_text=None, heading_anchor=None, padding=None, cursor=None, takefocus=None, style=None, width=1000, height=1000):
        Frame.__init__(self, master, class_="XML_Viewer", width=width, height=height)
        Frame.grid_propagate(self,False)
        self._vsb = Scrollbar(self, orient=VERTICAL)
        self._hsb = Scrollbar(self, orient=HORIZONTAL)

        kwargs = {}
        kwargs["yscrollcommand"] = lambda f, l: autoscroll(self._vsb, f, l)
        kwargs["xscrollcommand"] = lambda f, l: autoscroll(self._hsb, f, l)
       
        if style is not None:
            kwargs["style"] = style
            
        if padding is not None:
            kwargs["padding"] = padding
            
        if cursor is not None:
            kwargs["cursor"] = cursor
            
        if takefocus is not None:
            kwargs["takefocus"] = takefocus

        self._treeview = Treeview(self, **kwargs)
        
        if heading_text is not None:
            if heading_anchor is not None:
                self._treeview.heading("#0", text=heading_text, anchor=heading_anchor)
            else:
                self._treeview.heading("#0", text=heading_text)

        self._treeview.bind("<<TreeviewOpen>>", self._on_open)
        self._treeview.bind("<<TreeviewClose>>", self._on_close)
        
        # Without this line, horizontal scrolling doesn't work properly.
        self._treeview.column("#0", stretch= True, minwidth=100)

        self._vsb['command'] = self._treeview.yview
        self._hsb['command'] = self._treeview.xview

        self._treeview.grid(column=0, row=0, sticky=N+S+W+E)
        self._vsb.grid(column=1, row=0, sticky=N+S)
        self._hsb.grid(column=0, row=1, sticky=E+W)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._element_tree = None
        self._item_ID_to_element = {}

        if xml is not None:
            self.parse_xml(xml)

    def _on_open(self, event):
        item_ID = self._treeview.focus()
        if item_ID not in self._item_ID_to_element: return

        node = self._item_ID_to_element[item_ID]

        self._treeview.item(item_ID, text = self._repr_of_openning_tag(node))
        
    def _on_close(self, event):
        item_ID = self._treeview.focus()
        if item_ID not in self._item_ID_to_element: return

        node = self._item_ID_to_element[item_ID]
        
        text = self._repr_of_openning_tag(node) + self._repr_of_closing_tag(node)
        self._treeview.item(item_ID, text = text)

    def parse_xml(self, xml):
        self._element_tree = ET.ElementTree(ET.fromstring(xml))
        
        self.clear()
        self._walk_xml(self._element_tree.getroot())
        
    @property
    def element_tree(self):
        return self._element_tree
    
    @element_tree.setter
    def element_tree(self, element_tree):
        self._element_tree = element_tree
        
        self.clear()
        self._walk_xml(element_tree.getroot())   
        
    def clear(self):
        self._item_ID_to_element = {}
        self._treeview.delete(*self._treeview.get_children())
        
    def _repr_of_openning_tag(self, node):
        text = "<" + node.tag

        attrs = node.attrib
        
        # list function is here necessary to provide support to Python 3
        a_names = list(attrs.keys())
        a_names.sort()

        for a_name in a_names:
            text += ' %s="' % a_name
            text += attrs[a_name]
            text += '"'

        text += ">"
        return text
        
    def _repr_of_closing_tag(self, node):
        return "</%s>"%node.tag

    def _walk_xml(self, node, depth=0, parent=""):
        text = self._repr_of_openning_tag(node) + self._repr_of_closing_tag(node)

        item = self._treeview.insert(parent, END, text = text)
        self._item_ID_to_element[item] = node
        
        if node.text:
            text = node.text.strip()
            if text != "":
                for line in text.splitlines():
                    self._treeview.insert(item, END, text = line)

        child_nodes = sorted(list(node), key=attrgetter('tag'))
        for child_node in node:
            self._walk_xml(child_node, depth+1, parent=item)

        
        if node.tail:
            tail = node.tail.strip()
            if tail != "":
                for line in tail.splitlines():
                    self._treeview.insert(parent, END, text = line)


