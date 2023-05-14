import smartpy as sp


class HelloWorld(sp.contract):
    def __init__(self, message):
        self.init(message=message)

    @sp.entry_point
    def update_message(self, new_message):
        self.data.message = new_message

    @sp.entry_point
    def say_hello(self):
        sp.verify(self.data.message != "", message="Message cannot be empty")
        sp.verify(self.data.message != "Hello world!", message="Message already set to 'Hello world!'")
        sp.set_type(new_message=sp.TString)
        self.update_message("Hello world!")
        sp.set_type(self.data.message, sp.TString)


if "templates" not in __name__:
    @sp.add_test(name="HelloWorld")
    def test():
        scenario = sp.test_scenario()
        c = HelloWorld("Test message")
        scenario += c
        scenario += c.say_hello().run()
        scenario.verify(c.data.message == "Hello world!")
