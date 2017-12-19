from django import dispatch

pre_send = dispatch.Signal()
post_send = dispatch.Signal()
post_exception = dispatch.Signal()
