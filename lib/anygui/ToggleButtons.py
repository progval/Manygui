from anygui.Exceptions import UnimplementedMethod
from anygui.GenericButtons import AbstractGenericButton
from anygui.Models import BooleanModel

class AbstractToggleButton(AbstractGenericButton):

    #_text = "ToggleButton"
    #_on = 0
    _model = None

    # FIXME: When it works, the model stuff should be lifted
    #        to AbstractComponent

    def __init__(self, *args, **kw):
        self._set_model(BooleanModel())
        AbstractGenericButton.__init__(self, *args, **kw)

    # FIXME: Temporary solution. Shouldn't just be alias for model.value
    def _get_value(self):
        return self._model.value

    # FIXME: Temporary solution. Shouldn't just be alias for model.value
    def _set_value(self, value):
        self._model.value = value

    def _get_model(self):
        return self._model

    def _set_model(self, model):
        if self._model is not None:
            self._model.remove_view(self)
        self._model = model
        self._model.add_view(self) # FIXME: Should get all state at this point (?)
        self._on = model.value # FIXME: use 'not not value' or operator.truth?
        self._ensure_state()

    def model_changed(self, target, change):
        if target is self._model:
            for mname, args, kw in change:
                if mname == '_set_value':
                    self._on = args[0]
                    self._ensure_state()

    def _finish_creation(self):
        AbstractGenericButton._finish_creation(self)
        self._ensure_state()

    def _ensure_state(self):
        raise UnimplementedMethod, (self, "_ensure_state")
