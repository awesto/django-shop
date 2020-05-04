from elasticsearch_dsl.analysis import analyzer, token_filter

body_analyzers = {
    'default': analyzer('default_analyzer',
        tokenizer='standard',
        filter=['lowercase', 'stop', 'snowball'],
        char_filter=['html_strip'],
    ),
    'de': analyzer('german_analyzer',
        type='custom',
        tokenizer='standard',
        filter=[
            'lowercase',
            token_filter('asciifolding', type='asciifolding', preserve_original=False),
            token_filter('german_stop', type='stop', language='german'),
            token_filter('german_stemmer', type='snowball', language='german'),
        ],
        char_filter=['html_strip'],
    ),
}
