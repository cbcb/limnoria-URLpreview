# """This is a minimal example previewer intended as a starting point for new
# previewers. """


# from supybot import conf, log, registry
# from supybot.questions import something, yn

# try:
#     from supybot.i18n import PluginInternationalization
#     _ = PluginInternationalization('URLpreview')
# except ImportError:
#     def _(x):
#         return x

# from URLpreview.previewer import Previewer


# class ExamplePreviewer(Previewer):
#     def can_handle(self, domain):
#         '''Returns True iff this Previewer can handle the domain.'''
#         return domain == 'example.com'

#     def get_preview(self, plugin, url):
#         '''Returns a preview message for the url,
#            or None if the preview fails'''
#         return 'example.com is a domain reserved for documentation/examples'

#     def configure(self, plugin, advanced):
#         '''Called by config.py during the initial configure step'''
#         if yn(_('Enable example example.com previewer?')):
#             plugin.example_enabled.setValue(True)
#         return

#     def register_vars(self, plugin):
#         '''Called by config.py when the plugin is loaded.
#             Register your variables here.'''
#         conf.registerGlobalValue(
#             plugin, 'example_enabled',
#             registry.Boolean(False,
#                              _('Enable example example.com previewer?)')))
