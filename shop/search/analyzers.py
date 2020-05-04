from elasticsearch_dsl.analysis import analyzer, token_filter

html_strip = analyzer('html_strip',
    tokenizer='standard',
    filter=['lowercase', 'stop', 'snowball'],
    char_filter=['html_strip'],
)

german_analyzer = analyzer('german_analyzer',
    type='custom',
    tokenizer='standard',
    filter=[
        'lowercase',
        token_filter('asciifolding', type='asciifolding', preserve_original=False),
        token_filter('german_stop', type='stop', language='german'),
        token_filter('german_stemmer', type='snowball', language='german'),
    ],
    char_filter=['html_strip'],
)
