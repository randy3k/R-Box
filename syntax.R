library(stringr)

f = "syntax/R Extended.tmLanguage"
str = readChar(f, file.info(f)$size)
dict_begin = str_locate(str, "<key>support_function</key>\\s*<dict>\\s*<key>patterns</key>\\s*<array>\\s*\n")[2]
dict_end = str_locate(str, "\n\\s*</array>\\s*</dict>\\s*</dict>\\s*<key>scopeName</key>")[1]

template = "\t\t\t\t<dict>\n\t\t\t\t\t<key>begin</key>\n\t\t\t\t\t<string>\\b(foo)\\s*(\\()</string>\n\t\t\t\t\t<key>beginCaptures</key>\n\t\t\t\t\t<dict>\n\t\t\t\t\t\t<key>1</key>\n\t\t\t\t\t\t<dict>\n\t\t\t\t\t\t\t<key>name</key>\n\t\t\t\t\t\t\t<string>support.function.r</string>\n\t\t\t\t\t\t</dict>\n\t\t\t\t\t\t<key>2</key>\n\t\t\t\t\t\t<dict>\n\t\t\t\t\t\t\t<key>name</key>\n\t\t\t\t\t\t\t<string>punctuation.definition.parameters.r</string>\n\t\t\t\t\t\t</dict>\n\t\t\t\t\t</dict>\n\t\t\t\t\t<key>comment</key>\n\t\t\t\t\t<string>base</string>\n\t\t\t\t\t<key>contentName</key>\n\t\t\t\t\t<string>meta.function-call.arguments.r</string>\n\t\t\t\t\t<key>end</key>\n\t\t\t\t\t<string>(\\))</string>\n\t\t\t\t\t<key>endCaptures</key>\n\t\t\t\t\t<dict>\n\t\t\t\t\t\t<key>1</key>\n\t\t\t\t\t\t<dict>\n\t\t\t\t\t\t\t<key>name</key>\n\t\t\t\t\t\t\t<string>punctuation.definition.parameters.r</string>\n\t\t\t\t\t\t</dict>\n\t\t\t\t\t</dict>\n\t\t\t\t\t<key>name</key>\n\t\t\t\t\t<string>meta.function-call.r</string>\n\t\t\t\t\t<key>patterns</key>\n\t\t\t\t\t<array>\n\t\t\t\t\t\t<dict>\n\t\t\t\t\t\t\t<key>include</key>\n\t\t\t\t\t\t\t<string>$self</string>\n\t\t\t\t\t\t</dict>\n\t\t\t\t\t</array>\n\t\t\t\t</dict>\n"
filter = function(l){
    ind = grep("^[a-zA-Z\\._]+$", l)
    l = l[ind]
    l[nchar(l) > 3]
}
getfuns = function(pkg){
    filter(ls(pattern="*", paste0("package:",pkg)))
}
getregexp = function(pkg){
    s = template
    content = paste0(sub("\\.","\\\\\\\\.",getfuns(pkg)),collapse="|")
    str_replace(template, "foo", content)
}

library(data.table)
library(ggplot2)

packages = c("base", "stats", "methods", "utils", "graphics", "grDevices", "data.table", "ggplot2")

dict = ""
for (pkg in packages){
    dict = paste0(dict, getregexp(pkg))
}
str_sub(str, dict_begin+1, dict_end) = dict
cat(str, file="syntax/R Extended.tmLanguage")
