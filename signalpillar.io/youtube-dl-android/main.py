from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label


class MainApp(App):

    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        self._url_input = TextInput(
            multiline=False,
            readonly=False,
            # halign="right",
            # font_size=55
        )
        main_layout.add_widget(self._url_input)
        download_btn = Button(
            text='Download',
            # pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        download_btn.bind(on_press=self.on_download_btn_press)
        main_layout.add_widget(download_btn)
        return main_layout

    def on_download_btn_press(self, btn):
        url = self._url_input.text


if __name__ == '__main__':
    app = MainApp()
    app.run()
