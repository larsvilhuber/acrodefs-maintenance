# Tool to maintain my "database" of acrodefs

## Requirements

- shell to parse and run
- Python 3.12 to run consolidation
- gh to push to Gist.

## Available files

The resulting `acrodefs.tex` can be obtained as 

```
wget -O acrodefs.tex https://gist.githubusercontent.com/larsvilhuber/169753e43f3ef938c0db1410ffd34a44/raw/7c1032f0ff49af16a1fd08fab18a58e0b429c6b7/acrodefs.tex
```

or 

```
wget https://raw.githubusercontent.com/larsvilhuber/acrodefs-maintenance/main/acrodefs.tex
```

## Downstream usage

To use, include the following in your LaTeX preamble:

```
\usepackage{acronym}
\input{acrodefs}
```

## Notes

There may be better ways of doing this, but this works for me.