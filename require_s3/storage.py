import urlparse, urllib

from django.contrib.staticfiles.storage import CachedFilesMixin

from storages.backends.s3boto import S3BotoStorage

from require.storage import OptimizedFilesMixin


class FolderNameHackMixin(object):

    # HACK: Fixing handling of folder names.
    def url(self, name, *args, **kwargs):
        url = super(FolderNameHackMixin, self).url(name, *args, **kwargs)
        if name.endswith("/") and not url.endswith("/"):
            url += "/"
        return url


class NormalizeUrlHackMixin(object):

    # HACK: re-escapes the url coming out of Boto that has been unquoted by CachedFilesMixin
    # from http://stackoverflow.com/questions/11820566/inconsistent-signaturedoesnotmatch-amazon-s3-with-django-pipeline-s3boto-and-st
    def url(self, name, *args, **kwargs):
        url = super(NormalizeUrlHackMixin, self).url(name, *args, **kwargs)
        if isinstance(url, unicode):
            url = url.encode('utf-8', 'ignore')
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(url)
        path = urllib.quote(path, '/%')
        qs = urllib.quote_plus(qs, ':&=')
        return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


class OptimizedStaticFilesStorage(FolderNameHackMixin, OptimizedFilesMixin, S3BotoStorage):
    
    """
    A storage backend that optimizes with RequireJS and stores the result on S3.
    """


class OptimizedCachedStaticFilesStorage(NormalizeUrlHackMixin, FolderNameHackMixin, OptimizedFilesMixin, CachedFilesMixin, S3BotoStorage):
    
    """
    A storage backend that optimizes with RequireJS, applies a cached MD5 suffix,
    and stores the result on S3.
    """
