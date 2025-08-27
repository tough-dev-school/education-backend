from drf_orjson_renderer.renderers import ORJSONRenderer


class AppJSONRenderer(ORJSONRenderer):
    charset = "utf-8"  # force DRF to add charset header to the content-type
