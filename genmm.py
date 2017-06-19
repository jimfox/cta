#
# parse shepard data and build micromedex export file
#

import string
import re
import dbm

# files

input_data = ('catalog.tex','')
mm_data      = 'shep.dat'


#
# get next line 
#

def get1line(f):
   l = f.readline()
   if l=='': return ''
   l = string.strip(l) + '\n'
   l = re.sub('%$','',l)
   # print "[%s]" % l
   return l
 

def clean_tex(txt):
  h = re.sub('\\\\-','',txt)
  # bb and eb don't seem to be matched very well in the text
  # latex just ignores them
  # h = re.sub('\\\\bb','>>',h)
  # h = re.sub('\\\\eb','<<',h)
  h = re.sub('\\\\bb','',h)
  h = re.sub('\\\\eb','',h)
  h = re.sub('\\\\tm','',h)
  h = re.sub('\`\`','"',h)
  h = re.sub('\'\'','"',h)
  h = re.sub('^\$','',h)
  h = re.sub('(?P<d>[^\\\\])\$','\g<d>',h)
  h = re.sub('\\\\\$','$',h)
  h = re.sub('\\\\alpha','alpha',h)
  h = re.sub('\\\\beta','beta',h)
  h = re.sub('\\\\delta','delta',h)
  h = re.sub('\\\\gamma','gamma',h)
  h = re.sub('\\\\also','also',h)
  h = re.sub('{\\\\bf(?P<a>[^}]*)}','\g<a>',h)
  h = re.sub('\\\\b(?P<a>\d)','\g<a>',h)
  h = re.sub('--','-',h)
  h = re.sub('\^{(?P<a>[^\]]*)}','\g<a>',h)
  h = re.sub('\_{(?P<a>[^\]]*)}','\g<a>',h)
  if re.match('\\\\ag',h):
     h = re.sub(' *\\\\','',h[4:])
     # h = re.sub(' *\[','',h)
     h = '\\ag ' + h
     print '> ' + h
  elif re.match('\\\\nag',h):
     h = re.sub(' *\\\\','',h[5:])
     # h = re.sub(' *\[','',h)
     h = '\\ag ' + h
     print '> ' + h
     
  h = re.sub('\\\\%','%',h)
  # h = re.sub('\\\\','',h)
  return h

mm_file = open(mm_data,'w')
print mm_file

# process all files

for dat_file in input_data:
 if dat_file=='': continue
 f = open(dat_file, 'r')
 print f
 lnl = 0
 while (1):
   nl = get1line(f)
   if nl == '':
      break
   if nl == '\n':
      # print "lnl %s]" % lnl
      if lnl>0:
         continue
      lnl = 1
   else:
      lnl = 0
   mm_file.write(clean_tex(nl))
       
  
mm_file.close()


print "done"

