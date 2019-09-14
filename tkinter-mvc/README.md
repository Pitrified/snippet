# MVC implementation in Tkinter

Meld of https://gist.github.com/ajfigueroa/c2af555630d1db3efb5178ece728b017 that does not couple _view_ and _model_, and https://gist.github.com/ReddyKilowatt/5d0bfedbe9a92a8f50cd948ab51683ee that does not assemble the _view_ in the _controller_.

### Some notes:

The model knows nothing about the view or the controller.

The view knows nothing about the controller or the model.

The controller understands both the model and the view.

---

The model uses observables, essentially when important data is changed, any interested listener gets notified through a callback mechanism.
<!-- When `Model.addMoney()` is called, the registered callbacks are executed. -->

When a button is clicked, the bound callback `Controller.AddMoney()` is called, that in turns notifies the model of the changes through `Model.addMoney()`.
The model updates the Observable with `Observable.set()`, and the callback registered in the Observable is now triggered (`Controller.MoneyChanged()`), and only then the view is updated.

```python
class Observable:
    def addCallback(self, func):
        self.callbacks[func] = 1
    def _docallbacks(self):
        for func in self.callbacks:
             func(self.data)
    def set(self, data):
        self.data = data
        self._docallbacks()


class View(tk.Toplevel):
    def SetMoney(self, money):
        self.moneyStringVar.set(f"{money}")


class Model:
    def __init__(self):
        self.myMoney = Observable(0)
    def addMoney(self, value):
        self.myMoney.set(self.myMoney.get() + value)


class Controller:
    def __init__(self, root):
        self.model.myMoney.addCallback(self.MoneyChanged)
        self.view2.addButton.config(command=self.AddMoney)
    def AddMoney(self):
        self.model.addMoney(10)
    def MoneyChanged(self, money):
        self.view1.SetMoney(money)
```
