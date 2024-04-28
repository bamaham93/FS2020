from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Fieldset
from media.models import Media

"""
"""

class AddMediaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_id = 'id-mediaForm'
        self.helper.form_class = 'blueforms'
        self.helper.form_method = 'POST'
        self.helper.form_action = 'submit'

        self.helper.add_input(Field(label='title'))

        self.helper.add_input(Field('subtitle', 'subtitle'))

        self.helper.add_input(Field('isbn', 'isbn'))
        self.helper.add_input(Submit('submit', 'Submit'))
