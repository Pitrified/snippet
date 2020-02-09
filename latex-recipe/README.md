# My template for the final cookbook

### Features needed

Ingredients:
* ingredients as a list in the beginning of the recipe
* optional subtitles for sub-recipe ingredients
* ingredients list in a box, arranged like a wrapfigure

Body:
* numbered/labeled recipes
* numbered/labeled steps
* non numbered note step
* subtitle after recipe name
* final notes in recipe
* recipe source
* nice looking clickable urls in source

Book structure:
* title of the recipe in the TOC/[index](https://www.overleaf.com/learn/latex/Indices)
* title of the recipe in the header of the page
* chapter name in the footer of the page
* if printable, good looking two-sided magic
* some image support

Symbols/info in the recipe name:
* prep time
* serving size
* vegetarian (buuu)

### Resources

##### Existing packages

* good looking [template](https://tex.stackexchange.com/questions/366229/an-aesthetically-pleasing-recipe-book-template/366240)
* a broad [question](https://tex.stackexchange.com/questions/20549/a-cookbook-in-latex)
* `cuisine`: [ctan](https://ctan.org/pkg/cuisine), [doc](http://ctan.mirror.garr.it/mirrors/CTAN/macros/latex/contrib/cuisine/cuisine.pdf)
* `recipe`: [ctan](https://ctan.org/pkg/recipe), [doc](http://ctan.mirror.garr.it/mirrors/CTAN/macros/latex/contrib/recipe/sample.pdf)
* `cookybooky`: [ctan](https://ctan.org/pkg/cookybooky), [doc](http://ctan.mirror.garr.it/mirrors/CTAN/macros/latex/contrib/cookybooky/documentation/Manual.pdf)

##### On building a .sty package

* https://www.overleaf.com/learn/latex/Writing_your_own_package

Wrapping an itemize in text
* https://tex.stackexchange.com/questions/387315/wrap-text-around-table-in-itemize-environment
* https://it.overleaf.com/learn/latex/Wrapping_text_around_figures
