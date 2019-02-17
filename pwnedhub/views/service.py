from pwnedhub import db, spyne
from spyne.protocol.soap import Soap11
from spyne.model.primitive import AnyDict, Unicode, Integer
from spyne.model.complex import Iterable

class ToolsInfo(spyne.Service):
    __service_url_path__ = '/service'
    __in_protocol__ = Soap11(validator='lxml')
    __out_protocol__ = Soap11()

    @spyne.rpc(Unicode, _returns=Iterable(AnyDict))
    def info(ctx, tid):
        query = "SELECT * FROM tools WHERE id="+tid
        with ctx.udc['_spyne_ctx'].app.app_context():
            try:
                tools = db.session.execute(query)
            except:
                tools = ()
            for tool in tools:
                yield dict(tool)
