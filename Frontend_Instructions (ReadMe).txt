Mode of Inference (Example of data format)

Remarks: 
Kindly adhere to the format since regex is being used to check the appropriateness of the input parameters (for example: whitespaces, double quotes etc.).
If input format is wrong, assertion error will provide an example of the type of format to be used.

===========================================================================================================
# everything
data = {
    'mode': 'everything',
    'data': ''
}
===========================================================================================================
# box
data = {
    'mode': 'box',
    'data': '{"box_prompt": [[.0,.4,.7,1]]}'
}


===========================================================================================================
# text
data = {
    'mode': 'text',
    'data': '{"text_prompt": "This is a white cat"}'
}
===========================================================================================================
# points
data = {
    'mode': 'points',
    'data': '{"point_prompt": [[.3,.5],[.7,.3],[.4,.4]]}, {"point_label": [0,0,1]}'
}