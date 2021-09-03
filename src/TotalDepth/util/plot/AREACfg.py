#!/usr/bin/env python3
# Part of TotalDepth: Petrophysical data processing and presentation.
# Copyright (C) 2011-2021 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com
"""Module for plotting areas of particular patterns with well log data.

Created on 1 Apr 2011

Provides access to patterns either using the Data URI Scheme (https://en.wikipedia.org/wiki/Data_URI_scheme) or
as PNG files. Both can be in monochrome or RGB

"""
from TotalDepth.util import XmlWrite

__author__  = 'Paul Ross'
__date__    = '2011-04-01'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) Paul Ross'

import os
import typing


def png_location(pattern: str, is_monochrome: bool) -> str:
    """Returns the absolute path of the location of a PNG file for the pattern."""
    # B&W PNG files in: TotalDepth/src/TotalDepth/util/plot/patterns/PNG/mono
    # RGB PNG files in: TotalDepth/src/TotalDepth/util/plot/patterns/PNG/rgb
    sub_dir = 'mono' if is_monochrome else 'rgb'
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'patterns', 'PNG', sub_dir, pattern + '.png'
        )
    )
    if not os.path.isfile(path):
        raise ValueError('No file at path: "{}"'.format(path))
    return path


# TODO: Add map of LIS MNEM to AREA_DATA_URI_SCHEME_... key


AREA_DATA_URI_SCHEME_MONO: typing.Dict[str, str] = {
    'Anhydrite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAaElEQVR4nH1RSRLAMAgS//9nerCjBNPmkOASBQXJiABQ4AdHRNZDEoDhSm3/ZNsHrap+lK1J7dmU0krqudAj2R3rVmCh4a19d9U39FVSxYzcrVKVaRSAq7RhG6Xckz6IntHLLvcK23wA1quk0LliaAcAAAAASUVORK5CYII=',
    'Anhydritic Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nL3QOw4AIAgDUEu8/5VxIAFDispiR/k8IlR1PGdWBQDksbVbzmUT3CGcxU0g/Msl1uoDQsUkkN27SCejO4lVhIpJ+PInCznvPwfD+gA2AAAAAElFTkSuQmCC',
    'Anhydritic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nGP8//8/A17AyMgIV8OEJgEnsQIU1f///0c2iYBqiFISzIaTVAAIV+J3MRaXYDEMNZQIqEYLJcJmI4cSYbMZyA4lACKyKg2hg7mOAAAAAElFTkSuQmCC',
    'Anhydritic Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVUlEQVR4nM2QMQ6AMAwDz/n/n80QVCxSBCOeqtQ9u5FtSbYBIM9TBfSDtErqyVJPvlIvdmtaE3+GT2tfrEr5sff0bFjbxFTi/rOT4lmbhhOcG7w1PADedUsizsyUJgAAAABJRU5ErkJggg==',
    'Anhydritic Siltsone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVElEQVR4nM2SwQ6AMAhDX/n/f64HzGxEM4/2RKBrC5lsS7INAFlPFNAPkiqpOwvd+ap6aTcmNeVP80ntwYqUi+3dM2E9OiZS7j83Kd4xE262vP2LA1urSCmG/wtbAAAAAElFTkSuQmCC',
    'Argillaceous Dolomite'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nK2QQQoAIQwDHej/vxwPC25YIytibiVh2hRJLQmYLXwYtkfhzSRAop5oF/MsLJ/ddsq47Z99XoP4tZVqFY01kHTtwR91F4o1/hetDlYAAAAASUVORK5CYII=',
    'Argillaceous Limestone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPklEQVR4nGP8//8/A17AyMgIV8OEXykaYEE2A1kCq50s+KXRAGkuIQ0g/Ivsd+q4hAWXBNYgwqkaq6toGSYAn/gYD7R8kV0AAAAASUVORK5CYII=',
    'Argillaceous Sandstone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nM2PwQ6AMAhDXxf//5frAbOAiRvGi1yAAi0FAGzb3taaTSdGJEmS1jXwjvsIggzl+9voP3+P/ipwqUyFJ8eBf3ZZpCt+AmFmLSK0wJtTAAAAAElFTkSuQmCC',
    'Argillaceous Siltstone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nM2OQQoAIQwDp+L/vxwPqyWuh2UFwRwKTWCSkAQAEcFQmo8vqV8PPlUc7PjVAf6x6+v3lV6ywz65uzgsNfGs5J7dDS5HJDh/Lmr4AAAAAElFTkSuQmCC',
    'Argillaceous and Sandy Dolomite'            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nK2QWwoAIAgEd6D7X9k+AhMrjGj/fM2qmJl2Ak4lSbKgEXp+IlZAQb3XLWYYkrI+DHjou9Xs9zOI1iWjra1p48z+9uCkDlvYROjXVpJOAAAAAElFTkSuQmCC',
    'Argillaceous and calcareous Dolomite'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAT0lEQVR4nK2PwQ7AMAhCIdn///LrwYStZl0PHQcTFUEM6A22VytJAmqdmskt0Xs7B6f4fG72BK7nA0EkipTEG+2jGG6mG3YZNeoyRuv/xACGO0Tl0BNpPQAAAABJRU5ErkJggg==',
    'Argillaceous and calcareous Sandstone'      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQElEQVR4nGP8//8/AwMDIyMjhIEfMKLx4XoYGRnhXDibKCPhgImw7YwI+xmRHYBsO5o6ClyCZgxOV6Hxh2eYAAC7/zX+LIy0iAAAAABJRU5ErkJggg==',
    'Argillaceous and dolomitic Limestone'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGP8//8/A17AyMgIV8OEXykaYIEbgCyKy0IW/NJogDSXkAYQ/kX2O0IaVRCfSzD141ONaRVpvqRlmAAAqAsbC5l1GE4AAAAASUVORK5CYII=',
    'Argillaceous and dolomitic Sandstone'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nM2QwQoAIAhDe/3/P9shiLHUW5AnkfE2R0QMGcAuOrOSAoDtpIwK3/nenihs2zWf5OyT2OK5+nEnDfufThZZt0IJ/tvgJwAAAABJRU5ErkJggg==',
    'Argillaceous and sandy Limestone'           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARElEQVR4nGP8//8/A17AyMgIV8OEXykaQFHNyMjIyMiIRzULMoegq0hzCWkA4V9kv1PHJSy4JNACB2ItTtVYXUXLMAEAh1wVE0AhDJoAAAAASUVORK5CYII=',
    'Arkosic Sandstone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAU0lEQVR4nJ2RMQ4AIAgDW///ZxxIUApRI4sFSTmUZgaApIg21h1JAG0aOnUfXD3Ge2siOQCEfrJUkn4uqcKPOrqC3Ulk+wuJeA2v7oih96/4eZMJpTxCER54oxQAAAAASUVORK5CYII=',
    'Basalt'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nKWQwQoAIAhDXf//z+sQmMywME9uQ/YQJO15RhQAJHYnR/cBSQCRR2R0hpmtzbtEHp0WSU2lJPEsyz+SGmaTSLu8qAMzAQ/vQgoyST+KAAAAAElFTkSuQmCC',
    'Bedded Chert'                               : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATklEQVR4nI2QwQ4AIAhCwf//Zzq4VTOjTuLGmyAlASCZwmgAkUMSSa+X+xOIHX0CUW55IM5wBmhautyt4wYwl2kqDy6/dy373P/Au+W+DvSkeBHi/lYmAAAAAElFTkSuQmCC',
    'Bioclastic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nGP8//8/A17AyMgIV8MEF4KTeAATmlL8GpgYGBggFiGT+FQTqZRkgPAvst8JuASnYahex6caM6zwqcYMKwIuoSisAFjkKg3e92X5AAAAAElFTkSuQmCC',
    'Bituminous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8//8/AwMDAwMDIyMjAwMDnIsdYJXGpYeRJLMZCViNZgou1VjFSTObNHePjDABAMwPR9kAA/9PAAAAAElFTkSuQmCC',
    'Bituminous Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nJ2Q0QoAIAgDXfj/v7wehBLJRd2T5I2YIGkSAMsZ+RWATnp4OWNm3Ye+dtrbdnAt8Mzum7t3DL0uh3LhlZlkax8P1do588kEfokkH0pm3zIAAAAASUVORK5CYII=',
    'Bituminous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOElEQVR4nGP8//8/AwMDIyMjAwMDhE0a+P//P1wbGpuRJLMZ8avAbgou29HUkGY2ae7GAoZhmAAAIxdrtXg02vgAAAAASUVORK5CYII=',
    'Bundstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nK2Q0QoAIAgDW/T/v7weArEtkqA9hZ16CJKtCoCF9RLNeaOHL423SyqdodA9R/5ISkW78zyffTAJdde4mlm2C+aD1PTnTP+cJwY4AHxqAAAAAElFTkSuQmCC',
    'Calacareous Dolomite'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nGP8//8/AzbAyMiIKcWEqQiXUiyq8SglGRBrDMRCLC5BU4TsNgKqGSjxBkIfMWYw4Q9gdLMhFHUCGA0AACnbJAzVjj8tAAAAAElFTkSuQmCC',
    'Calcareous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOklEQVR4nGP8//8/AwMDAwMDIyMjnI0LsOCSYGRkJEE1VnuY8EujWcKC1UZcmlkI+gy7S4ixZGSECQDrIiEfT3Wc6AAAAABJRU5ErkJggg==',
    'Calcareous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUUlEQVR4nJWQSQoAMQgErTD//3LnEFBxRLBP4lJqI8lGAd5zAMALbRyTK/bnKTN72RznmTW7XhaF39HBzoBBpyyd/VmyG1OHDSt287ir+CPpArVPMzf2llZFAAAAAElFTkSuQmCC',
    'Calcareous and dolomitic Clay-Shale'        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nOVQQQ4AIAgK5/+/bAeXI7I+EDcGAxQRMRYAMD3hbGVB6ObOVHa0JcbabUalNHWSndak/j5LFlrbKA2V+MdPJiIDPByHWYwhAAAAAElFTkSuQmCC',
    'Calcareous and dolomitic Sandstone'         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nGP8//8/AwwwMjIiczEBE7JSZAlGRka4CJwNNQxiKrFmQxRhVYpsJxNWG3E6D4/VmM5jQpNG5mI6b2SECQBMjTw4JXDMKAAAAABJRU5ErkJggg==',
    'Cargneule'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nJWQwQ4AIAhCof//Zzq0NTWzfCdniBglwUNyN20NYBTSk6gOSCJZa65wTYfttzyPJNF7hUseynP/vK1B6mebo5bCf2Lvyh4TfOQtAyob3cMAAAAASUVORK5CYII=',
    'Chalk'                                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMElEQVR4nGP8//8/A17AyMgIV8OEXykaGDyqGTB9+R8GMMUR/kX2O3VcMnhUkxYmAJvLKe+Ae3r8AAAAAElFTkSuQmCC',
    'Chert'                                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPElEQVR4nGP8//8/A9GACZnDyMhIrGpGRsb////j18CEbCoyiRUwku9u+qpG8wM+1ZihhFM11lCiZZgAAPxiDyvOsiCbAAAAAElFTkSuQmCC',
    'Cherty Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nGP8//8/A17AyMgIV8OELIpfG0I1RClBDVDVELsIugrhEoJKSQYI/yL7nbBLcJqH5HUCqtHCioBqtLAi7BLywwoAi+8eDTGrwIsAAAAASUVORK5CYII=',
    'Clay-Shale'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALElEQVR4nGP8//8/A9GABZcEIyMjFkGSzGYiXikDAwMW6yAAq520dMnICBMADGcVBzMaN78AAAAASUVORK5CYII=',
    'Coal-LigNite'                               : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAD0lEQVR4nGNgGAWjgDAAAAIoAAGcWSSWAAAAAElFTkSuQmCC',
    'Coarse Sand'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARElEQVR4nL1QQQoAMAjS0f+/3A6BwYioy7qUVCrS3TEu00QSgJ5LeObEALhywmi9AUF7uHupnZNdJnndi8T2ZyalAdUFfLM7/07GoPYAAAAASUVORK5CYII=',
    'Coarse Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAM0lEQVR4nGP8//8/A9GABc5iZGRkYGCAa8bKZSLeYAYGBkaSXMIIofA7AM6lpUtGRpgAAM5kKgsMUAyuAAAAAElFTkSuQmCC',
    'Diatomite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAO0lEQVR4nGP8//8/A9GAiYGBgZGREVkIwkUThIpgNRuXhYwkuYSwecjiLBAO3JVoetDESXPJMA0TND0A3AM1/D7zDSwAAAAASUVORK5CYII=',
    'Dolomite'                                   : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPElEQVR4nGP8//8/AzbAyMiIKcVEvFLsqnEpJRkQawzEQuzuxqqUAZcvsSolGSD0EWMGE0nWMVHkMvwAACCDJAfDNFd8AAAAAElFTkSuQmCC',
    'Dolomitic Caly-Shale'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQElEQVR4nGP8//8/AwwwMjIiczEBCy6ljIyMmKqhKgiaCgFMEAq/Urg9WKxD049sLQEHoLmQCauNmDZAwMgIEwALgzkHzhgjEAAAAABJRU5ErkJggg==',
    'Dolomitic LimeStone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANUlEQVR4nGP8//8/A17AyMgIV8OEXykaoI1qRkZGYlUjO50EgNBEjAH0DBOI34lSTabfcQEAi7MSE+ir8tcAAAAASUVORK5CYII=',
    'Dolomitic Marl'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nKVQQQ4AMARrxf+/bAc7iDCS9VhVWpoZ1tBuQLIgkzeZmQjZSwEU5xzl2mCWzsosDB+23qtO8MyqSYcm3xV0g69OHAfMlyoDZ++y9AAAAABJRU5ErkJggg==',
    'Dolomitic Sandstone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nNWQQQoAMQgDM/v/P6cHodRQhB43p6ASh2AbkGRbElDmqrY7TyOifFsPqaVvuwkA2jWwR6dPvPl74BEYf+pkKCTxnjpZrspLEYf/PmsAAAAASUVORK5CYII=',
    'Evaporite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAI0lEQVR4nGNgYGBgYGD4//8/MQwmItUxkGQqAzIYdcmgdAkAGBqzVe8WCnAAAAAASUVORK5CYII=',
    'Ferruginous Sandstone'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAXUlEQVR4nI2PUQ7AMAhChez+V3YfZMRUa+ZPK634QGbG72JE4CtJvri18uioG5Zt7AbVVcOep/32AJpkV/sS452/94IBANxgHGD2PmCcav6ttx6APZbbCinxyjpyvwwRMyfVPyeZAAAAAElFTkSuQmCC',
    'Fine Sand'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMUlEQVR4nGP8//8/AwMDIyMjhIGfjeAQA5iIV8rAwMDEyMgI5xBk09QlRLqBYQSFCQAmDhgsJpWEewAAAABJRU5ErkJggg==',
    'Fine Sandstone'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMUlEQVR4nGP8//8/AwMDIyMjhIGfjeAQA5iIV8rAwMDEyMgI5xBk09QlRLqBYQSFCQAmDhgsJpWEewAAAABJRU5ErkJggg==',
    'Glauconitic Sandstone'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nOWQwQoAMAhCff3/P7dDEK1gY+d5MhGVcHdJQJAzLK1ASEDyRIg8Z0s6WGuPtd55biOvA+pIm3UNNe6PnyyqGzNBATWL9wAAAABJRU5ErkJggg==',
    'Grainstone'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAS0lEQVR4nK2QSQ4AIAgDqfH/X8YDl1pwS+wNmZSJcHc7BUBg7Yhy3uiej/IonkpnYpngmNbusikew4qBwkTUp9WtpZnJD25aC/pzBrbHIQlJW8yGAAAAAElFTkSuQmCC',
    'Granit'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAWElEQVR4nIWRQQ4AIQgDB+P/v1wPawwCi9zQaaFqkgDAzIDTnvLnJunrfWXNVj69a7q+vi1+6XK9a+8+IjAz58VBPzzUDIl0sC8FIxvvQCklzxck/2XP+VqGakf+4p+XOgAAAABJRU5ErkJggg==',
    'Gypsiferous Clay-Shale'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nOWQQQrAMAzD5P7/z9phUNKu0NznQzAJWCZRk6gAUP1B6nuec26+aqcCMCpkT0qOvtvwTq8Nx5W4xP3iJw8IpGvEnZM5aQAAAABJRU5ErkJggg==',
    'Gypsum'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nOVQyw4AIAgC/v+f6eBWzFrrHienPFQCsI0AydaZkG2SL1QAKu8SJDUtZkdVlSBdj5nKcTPbM4UrWqaO+zXBuvKLnwzV/lcSOs5hDQAAAABJRU5ErkJggg==',
    'Halite'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAM0lEQVR4nGP8//8/A9GACb80IyMjFtVoomSajQZYCKqAW/v//39GiC+RXYLH34yjYYIBAEA0GBmFK8p6AAAAAElFTkSuQmCC',
    'LimeStone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAKUlEQVR4nGP8//8/A17AyMgIV8OEXykaGDyqSQMI/yL7nTouGTyqSQMAz4wMDa/28hkAAAAASUVORK5CYII=',
    'Marl'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANUlEQVR4nGP8//8/A17AyMgIV8OISzUjIyMWQYJmIwMm/Iahm41LAqud5LoEp+1ILhwZYQIAnxceBD5KjswAAAAASUVORK5CYII=',
    'Medium Sand'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nL2QMQoAIAwDL/7/z3EQihSK1cFMKQ3hiGwDgCRgnaWPdEcjildH8vl11U2kbR/9E3dT2nmq4eL8RlIBPG4yATezQfd5uw3DAAAAAElFTkSuQmCC',
    'Medium Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOklEQVR4nGP8//8/AwMDAwMDIyMjAwMDVi6czQiXJgYwQbRCdKOxsXBJNpugqXD2yHA3VDcxMUqy2QDFpidB0n15kwAAAABJRU5ErkJggg==',
    'Metamorphic Rocks'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAZElEQVR4nI1QQQ7AMAiSpf//Mju4qYUumScroFCQjAgA1cRbOakCsGKvyUglyW7yUaQCpqbRiYkfdwKn+tbNiZ77NqYpk1okubaOHvw3HyeC/Up59O2aS9RyOjPIvBd4spqQvAHySX3yFrLg2wAAAABJRU5ErkJggg==',
    'Monogenic Breccia'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOklEQVR4nGP8//8/A17AyMgIV8OEJoGpFFmcCZcEVsCERw5ZJ9QsiJvQjMTlGUaCviTWJZjuGRlhAgAtLRgyEcKORwAAAABJRU5ErkJggg==',
    'Monom Conglomerate 2-4 mm'                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUklEQVR4nK2PQQrAQAwCY+j/v2wPllCIay/1smAmGwXJigJQVcJ6LLkbJUlS095W0JXH84WS4HleVupwIux+n1DbxNMfSfZdmwQ6Nzu56E9JrG6qhkIGGTVhsAAAAABJRU5ErkJggg==',
    'Monom Conglomerate 4-64 mm'                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nJWQQQoAMQgDndL/fzk9WJbdtQXjxSAGxyAp2jWzASkec53sbeC9JKlOUo8+RkRsX5ME60uPZN6OHnn4sX4oSzJ+JgaJlckCnmc/B2uMdZEAAAAASUVORK5CYII=',
    'Mudstone'                                   : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nGP8//8/AyHAyMgIUcZEUCkyoEw1IyMjVjZOsyGKMJWiA4hXMEk4YMEaJsiCyGzSfMlITHhjN5ugz0hzCWkAAKToHgkrRAs6AAAAAElFTkSuQmCC',
    'Nodular Limestone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nGP8//8/A17AyMgIV8MC4aOpwGUEC7JWrOahqP7//z8JZuORoxQg3IfLreguwW4MNs9gV40roLCrxhVQOF1ChYACANrKLRS2iQ6vAAAAAElFTkSuQmCC',
    'Oolitic Limestone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUUlEQVR4nKWQQQoAIQwDJ9L/f7l7ECTUtQvunFoJaYwyE5AEAHN1JK3HKLvPO8M9TqIXdWO5iKlrct/z8b9yMzqnravRqIs93skJj9cl+dvVA4fxMA96Yh44AAAAAElFTkSuQmCC',
    'Organic Shale'                              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAI0lEQVR4nGP8//8/AwMDIyMjAwMDfjYDAwMTAylgVPXwUQ0AB0MMFSP+cO0AAAAASUVORK5CYII=',
    'Packstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nKWQQQoAIAgEM/r/l6eDIGWWSHMSWXVdAVqGiKisp9KVmnqcR7UIHQa7AcDGrqz7dMZfdi17P+Qvk3f8mzr9rOakxgTNOSEDX8Wr9AAAAABJRU5ErkJggg==',
    'Pelletic Limestone'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGP8//8/AwwwMjJCGGiCcC4LVlFkNjJgwhTCA0hTjXDJ////sbqbfIDTZ1jtYWHABnCFD33CBBlQJ3wAmIMqD4E2qgIAAAAASUVORK5CYII=',
    'Phosphatic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nGP8//8/A17AyMgIV8OELIpfG0I1xACCGqCqIUoJugrhEoJKSQYI20lzCU7zkLxOQDVaWBFQjRZWhF1CflgBAI1EJA08NnvVAAAAAElFTkSuQmCC',
    'Plastic Clay-Shale'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nJWQQQoAIBACM/r/l+0QLLthxnoeBxEkxzsAMrAMGoUG7dxhkgunlJHMA9ySw0m3oDN3dcQSE/i/R33wT5fml8i6nnsDfW8nCZgs+fUAAAAASUVORK5CYII=',
    'Polym Conglomerate 2-4 mm'                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVUlEQVR4nJVQ0QoAMQjSuP//ZffQEWMrYb4UZqFREixIAkhZFJXsLZUkKadR23sz4fPjuppO+JeNchkmRbsfRoorSa+e0H+wDBxOmKkrqw/65uTtgwsd/DMWI7a1KwAAAABJRU5ErkJggg==',
    'Polym Conglomerate 4-64 mm'                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUElEQVR4nJWQSQ7AMAgDPVH+/2V6QIlI2kqYC4hFHkxEqB0zE5DFPn53JI062DUQK+p09DEkkUJNEqwvPZL5J/rJw8V6UBY3cs33xCCxPHkAgtY5CGimDAUAAAAASUVORK5CYII=',
    'Polymictic Breccia'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOklEQVR4nGP8//8/A17AyMgIV8OEJoGpFFmcCZcEVsCERw5ZJ9QsiJvQjMTlGUaCviTWJZjuGRlhAgAtLRgyEcKORwAAAABJRU5ErkJggg==',
    'Quartzite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nKWQQQrAMAgEZ0P+/2V7CEhK3RLJnkaRZVARAQCSkl3Guss5WdKX1erupe52bL1LHsCue8J979fWeZd/dd7zR+7W+wGx+TkdMcwj/gAAAABJRU5ErkJggg==',
    'Radiolarite'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nJWQQQ4AMAQEbeP/X9aDxmHRMCeJiQXMTCoARCtqdLZLXoRzOpW8kR3jHf14u70zh+IomgNfRDq/nT3x2P7v4Kg055fsfnIBINwtDxqvwyoAAAAASUVORK5CYII=',
    'Reefal Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVUlEQVR4nKWQQQoAIQwDk+L/vxwPsllptbDsHIsZQygJAEk8rIsh6Uv4qaSaTAxHnUm+ndi/k9SIAZwdt97feHPVUYeKpgDKUKPvmoa6unEaquv9lwkkmkUMomLlzQAAAABJRU5ErkJggg==',
    'Saliferous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAO0lEQVR4nGP8//8/A9GAhYGBgZGREVMPIyMjpmrG////o0ngsQ2LqXgAFuvgNmC6EJ/ZmC4kzSUjI0wAFFA1+6keiUkAAAAASUVORK5CYII=',
    'Saliferous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUElEQVR4nLWPUQrAIAxDk93/zvGjrkt1QwSXD5FneY2UBAAASdxJGFxSP/1hmcvFrk9S4NIdHYp7Vg6w53Dvl+mI74n7sPmZpuXrJ3/23nM3IHwnQHeS6oUAAAAASUVORK5CYII=',
    'Sandy Clay-Shale'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANElEQVR4nGP8//8/A9GABc5iZGRE1snIyIipmpEks5mIV8rAwIDFOgiA24nsQlq6ZGSECQDZPyEHwUroqgAAAABJRU5ErkJggg==',
    'Sandy Dolomite'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nK2QSQ4AIAgDHf7/53ow0QRwCbFHCkMBSS0TEC2bHhBbfT0CUmpFr5ixMM+9y3Zn189Ycy8MO7TGY5D07cFOHda6LROws8HIAAAAAElFTkSuQmCC',
    'Sandy Limestone'                            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nLWQSQoAMAgDneL/v2xv3VCL0OYWmMMkmJmkAQbTcvTIRgNAQutarlY1k1rm3nX7G5OQdv9RF5Xgn5+fdNxMEhcEcvnvAAAAAElFTkSuQmCC',
    'Sandy and calcareous Clay-Shale'            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAN0lEQVR4nGP8//8/A9GABc5iZGRkYGCAa4Zw0QAjSWYzEVSBbAkLVhuRnYQMWKjsEmTjRkaYAAAsDx4cGeIBrAAAAABJRU5ErkJggg==',
    'Sandy and calcareous Dolomite'              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAT0lEQVR4nK2QUQrAMAhD+7z/ndMPwYGmlLHlR9AQkyBpOQDzFHkAijSpRegCuT09fAdjzvNAUkxz01jFuGh/ivFo24Ibwha8TjFy/FNwwwbTbSocsEZF/gAAAABJRU5ErkJggg==',
    'Sandy and dolomitic Clay-Shale'             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nK2QQQoAIQwDO4v///LsQVARkRbMKZcm06BGVeo4W/0mktmA+pUQuLBtwQWSrhrJ7H25SUQAWZL+aIPzLMfOFMlY8AfINzjqFkg+IgAAAABJRU5ErkJggg==',
    'Sandy and dolomitic Limestone'              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nK2QQQ4AIAjDrPH/X8abgCQzRncDStjAzJoUsJiu0U2JBgBBj1gcXd05uZPnjdl9nJvKSd1XdD318O/Pmn14GA9NwmSYAAAAAElFTkSuQmCC',
    'Sandy, calcareous and dolomitic Clay-Shale' : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANElEQVR4nGP8//8/A17AyMgIV4PEQhKFcLHoJGg2MmDCbxi62bgksLqQXJfgtB3JhSMjTABr/ioEg6lPggAAAABJRU5ErkJggg==',
    'Shelly Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nKWQSQ4AIAgDi+H/X64HEyQSG5eeh6VjJCFjZsE0jS5pYzpvErQDIBmQfsxPoMfMvrn7LvdOtneLKxd0daVofLrqo68eFd3YGfQAAAAASUVORK5CYII=',
    'Shelly Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8//8/A/EAovr///9wBrI4GoMRwmFkZESWwAUYyXEJsmPwOA+f2ZjOI8slwzxMAG47d52ba7dLAAAAAElFTkSuQmCC',
    'Shelly Siltstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVElEQVR4nKWRUQrAIAxD83b/O2c/o9a6aWH5EEnLI0Zsq61LEhBnURlR2PA4cdmxbQN5NU9fALvcNVkmzeaZHfFa2zWJ5u7WNn+8soMcZu7166dCNyAFKkIfds7/AAAAAElFTkSuQmCC',
    'Silicified Claystone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMUlEQVR4nGP8//8/A9GABZcEIyMjFkGSzGaCmAE3CY2LbjYuY7DaSaJLiFfKMFLCBAAlGxUfmF8FdgAAAABJRU5ErkJggg==',
    'Silicified Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOElEQVR4nGP8//8/A17AyMgIV8OEXykaoINqRkZGXAw4wBQhABD+RfY7AZcQCWiqGo/f8YQPUQAA4vQMJb354DUAAAAASUVORK5CYII=',
    'Silt'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAL0lEQVR4nGP4//8/AwPDfxiAsHGJMEJYRAImCMXIyAgn8YiQbjZBIxHkqLspdDcAZH0wLFPZPesAAAAASUVORK5CYII=',
    'Siltstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAN0lEQVR4nGP8//8/AwwwMjL+//8fQjIgAbg4ugR+wMTIyAjRjSaBVZxEswmahyw+6m5McdLMBgBrER489RV4aAAAAABJRU5ErkJggg==',
    'Silty Clay-Shale'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANElEQVR4nGP8//8/A9GABUIxMjJCtCEzMFUzkmQ2E/FK8YH///9DrIWT////p6VLRkaYAACSqzjtRF5cLQAAAABJRU5ErkJggg==',
    'Silty Marl'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8//8/A17AyMiIUPP//38IB5OBRSdBs5EBE7KNxGtDB8gOg3PJdQkugOLCEREmANZgU8Q4u680AAAAAElFTkSuQmCC',
    'Silty dolomitic Marl'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUElEQVR4nJWQwQoAIAhDM/z/X34dBJGy0h1MaXOqAKMMtUdETBaTK/t0SD1nLLxxG4ApPQLVZmY7/8Q4YXTckkR2fjx21Y03Lrf7IJ2wd+AFwKZW1gNuI3wAAAAASUVORK5CYII=',
    'Silty, calcareous and dolomitic Clay-Shale' : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8//8/A17AyMiIUPP//38IB5OBRSdBs5EBE7KNxGtDB8gOg3PJdQkugOLCEREmANZgU8Q4u680AAAAAElFTkSuQmCC',
    'Slaty Shale'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAF0lEQVR4nGNgIAUw/v//nyQNo2YPE7MBOnkR9WfXtEsAAAAASUVORK5CYII=',
    'Sylvite'                                    : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPElEQVR4nGP8//8/AzbAyMiIJvL//38WXBJwElkzC7I0mqmYprDgsReL83C5GytgIl4pyapZcEkMqxAEAKK0JyFFk7iqAAAAAElFTkSuQmCC',
    'Void'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAF0lEQVR4nGP8//8/A9GAiXilo6qHlWoAh/ADFdofhqIAAAAASUVORK5CYII=',
    'Volcanic Rock'                              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAWklEQVR4nH1RMRLAMAiC/P/PdrD1jEJdIokcYBgRAEgCyD5h9b2Yx34b/Pdy4iVywe5EinSOHpK+6dI4wvnT/ezpafJS2wTKfTtLp/DYWlVXMH9mpGbKmpMpHxDDVALaMndxAAAAAElFTkSuQmCC',
    'Wackstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARElEQVR4nGP8//8/AyHAyMgIUcZEUCkyoEw1IyMjVjY5ZqMAiFcwSYRt6HxGRogiOIOAS7Cait1s/ADFbMxAwKeaygAAffUkAKd7KGIAAAAASUVORK5CYII=',
}


AREA_DATA_URI_SCHEME_RGB: typing.Dict[str, str] = {
    'Anhydrite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAVklEQVR4nH2RQQ4AIAjDKi/f0z1gjIEhpxlGGXEJAEGKjwbi49Dk7pgyk7VoJpwvdRTkWyaeBp5cy+fuWiVoQb7xbstcqWa6z+iYacnJbQfsDeNf2oUboJQsEiXX+zgAAAAASUVORK5CYII=',
    'Anhydritic Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nGNk+M9APGDBKcOIVYwUs5kIyDOi2IPNPgiA28mIYBNyCUQpTAMTQhSrTf9R7GHEaiMuN8JUo9qIC8Bcgmojug30CBMAeYQVD4o5gkoAAAAASUVORK5CYII=',
    'Anhydritic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARklEQVR4nGNk+P+fAT9gZISrYUKXgJPYAKrq//+RTSKkGqKUBLPhJOUAyZV4XYzNJVhMQwklQqpRQ4kIs5FCiQizGcgNJQARKhwPcs9vVAAAAABJRU5ErkJggg==',
    'Anhydritic Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAU0lEQVR4nM2QMQ6AMAwDffn/n8uQFlyMBCOeUst1TmFISENTPqdKUn/wKMs51Q4fW6/uVkaJmYxiDotzPl+3O2E9bnR53X9uUpHZiJPwXszuOOEBckQZGAlq4VQAAAAASUVORK5CYII=',
    'Anhydritic Siltsone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUUlEQVR4nM1Syw4AIAgC//+f62APirY6xskYITpZAAIFDVo7AkB+UCk7M5AMH12nd8KltJoupTDsOdvz2l0TxrGjQu3+2UmYZkm8JbxMud1FBUXMGBsovyvyAAAAAElFTkSuQmCC',
    'Argillaceous Dolomite'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARElEQVR4nK2Q0QoAMAgCFfr/X3avsgy2sXuLDiMpZAj0FX1QUt1gDJgO3hGyswcIKJ8dNfUo+/0NxtYmalLjG9THgjcWe7cSCvbhSg0AAAAASUVORK5CYII=',
    'Argillaceous Limestone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPUlEQVR4nGNk+P+fAT9gZISrYSKgFBWwoJiBDLDZyYJfGg2Q5hLSAMK/yH6njktYcMpgCyLcqrG5ipZhAgAYfRATjEDoEAAAAABJRU5ErkJggg==',
    'Argillaceous Sandstone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARklEQVR4nM2POw4AIAhDH8b7XxkHg0GMUeIiC7R8WgAABYVjLQPcROlJQIza1WRvV+ZtnNG19Y/vkhk2HQ3YIvDPXwZpzzfo2Q8YiExSawAAAABJRU5ErkJggg==',
    'Argillaceous Siltstone'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQElEQVR4nGP8zwAFjAwI8B+JzcjA8B9OIksQBEzIBiMbjynCQKrZLGh8ZFciW0KO2bR0NxOyYXCEYh4yOWjcDQCBFAwgHEWPsQAAAABJRU5ErkJggg==',
    'Argillaceous and Sandy Dolomite'            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nK2Q0QoAIAgDb9D//7K9xTDDiEYv5jxXCmoJTi2AsINZfUY7oKHeq2DXPghQug1rr3Jl69nvz5Cvbhljt6bEmf3tg5MmPlAXAPSeNDAAAAAASUVORK5CYII=',
    'Argillaceous and calcareous Dolomite'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nK2QMQ4AIAgDj8T/f7lOEmg0DnobUKAQYk/AqQSgVVYJrSE8Lg2v+OyjDgSjGkjURXnxZfbTGWFLL2q6s2ogkeX/PNiYTeAW/2hSCdYAAAAASUVORK5CYII=',
    'Argillaceous and calcareous Sandstone'      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAPElEQVR4nGP8z8DAwMDAyMAAYeAHjGj8/6gS/1HZjMQYCQdMJNnOiOwAZNsxXUmuS9A9S4SrsDhjmIQJAAhEEgryKgR1AAAAAElFTkSuQmCC',
    'Argillaceous and dolomitic Limestone'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAP0lEQVR4nGNk+P+fAT9gZISrYSKgFBWwIAxABjgsZMEvjQZIcwlpAOFfZL8jyaMI4nUJhn68qjGsIs2XtAwTAMapEg8CuYDQAAAAAElFTkSuQmCC',
    'Argillaceous and dolomitic Sandstone'       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQElEQVR4nM2QMQ4AMAgCuf7/z3bVit2alMkYchAIFSEdn6w1WZFoN3Ka8FxyeyYZhgOXepZt+0V3P97kwv5nkw3rORYNwNNdvQAAAABJRU5ErkJggg==',
    'Argillaceous and sandy Limestone'           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nGNk+P+fAT9gZISrYSKgFBWgqmZkZGBkxKOaBYVHyFWkuYQ0gPAvst+p4xIWnDJogfP/P17V2FxFyzABALKBDhX5fG2HAAAAAElFTkSuQmCC',
    'Arkosic Sandstone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUElEQVR4nJWQMQ4AIAjEiv//sw4kBAEVmSpeoCoTAIEAZYndCeCi/mi8pS9TtUY/uplcBIxjumVS7z1BXp3F3ibh9Q+TMGto15sZz9T8+5MFBPEWEca8V1MAAAAASUVORK5CYII=',
    'Basalt'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nKWQUQoAIAhDtZPt6DtaH4HJjIryy23IHjpJu56WBQCJw6nReZwkgMwjMjvNzMYWXSKXzhPJnkpJ8lmVfyR7mEki7fKiF5gOHrNBTZ7KUq8AAAAASUVORK5CYII=',
    'Bedded Chert'                               : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATklEQVR4nI2QwQ3AMAgDz+y/M31EVZIWnLwwiBM2SgAEQxgNxCgJekedntuXQKzoEYjPLQ/E35wBipTOd7nRAWL/qPpWPmXt+x44p1zbBzZvKBUs1RpzAAAAAElFTkSuQmCC',
    'Bioclastic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nGNk+P+fAT9gZISrYUIIwUncgAldKV4NTAwMDFCLkEl8qolTSjJA+BfZ74RcgtM0FK/jVY0RVnhVY4QVIZdQElYA3+wcDxvV3xQAAAAASUVORK5CYII=',
    'Bituminous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMElEQVR4nGNk+M8ABYwMDAwMCC52gFUahx5GksxmJGQ1mim4VGMTJ81s0tw9MsIEAKEAF/lTN2ofAAAAAElFTkSuQmCC',
    'Bituminous Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATElEQVR4nJ2QQQoAIAgE3fD/X7ZDkSa5UXOSnCVWiJlwgOW07RXgQZ1ezIhUH6rvqBfswbXAK943dq9ofJ0OpcxLs1ltnw5V2zHzRwdUshgf/EnncAAAAABJRU5ErkJggg==',
    'Bituminous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8z8DAwMDAyMDAwMAAYZMG/iNpQ2MzkmQ2I34V2E3BZTuaGtLMJs3d2G0cbmECADdBI+1BCY0mAAAAAElFTkSuQmCC',
    'Bundstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nK2QQQoAIAgENfr/l+0QyeZaEjTHmmxQxUxKVKfWahV4s3vyqUORZKO0cg+EO7NwQq9xHs3OSjydMu5lkX2DuJDa/ssAp9oaDL2GU5YAAAAASUVORK5CYII=',
    'Calacareous Dolomite'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nGP8z4AdMDIwYEoxYSrCpRSLajxKSQaMRBoDsRCLS9AUMSC5jYBqBkq8gXA3MWYw4Q9gTFcxMFArgNEAANH+DA73HLsfAAAAAElFTkSuQmCC',
    'Calcareous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMklEQVR4nGNk+M8ABYwMCDYOwIJThpEk1djsYcIvjWYJC1YbcWlmIegzHC4hwpKRESYAweELJQ+2Dv8AAAAASUVORK5CYII=',
    'Calcareous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nJWQMQ4AIAgDW+L/v4yLIkHE0ImAXLFUfETA3ggBukFan80We1gLu+trv9Nmx9ueA8/mZZ1KgmmdT5OdhFo4tNjp15dCPgpMCHYRH760x+QAAAAASUVORK5CYII=',
    'Calcareous and dolomitic Clay-Shale'        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGNk+M+AAIwMKFwMwIKiFBmgcVFUQ0xFVoHNEiYUOVzOYESjMQFcJyOCy4LfW2guZEKXw2oDzMSRESYA0I8UIIfrpeAAAAAASUVORK5CYII=',
    'Calcareous and dolomitic Sandstone'         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAP0lEQVR4nGP8z4AAjAwMyFxMwISsFBkwIonA2Yz/kUwl1uz/SCQaQLaTCauNOJ2Hx2pM5zGhSSMDTOeNjDABAJLuFCBieVyyAAAAAElFTkSuQmCC',
    'Cargneule'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nJWQSQ4AIAjECv//M14RYdSeCJmUxYKKQXQ14CJ6UtOFANMJgUU3fdrnskl1M2j0uW/uLGh9uek6yv7Evyv/WPAuDwvuO4DZAAAAAElFTkSuQmCC',
    'Chalk'                                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMElEQVR4nGNk+P+fAT9gZISrYSKgFBUMHtUMWHz5/z8UYYgj/Ivsd+q4ZPCoJi1MAAyfG/u/D9DFAAAAAElFTkSuQmCC',
    'Chert'                                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANUlEQVR4nGP8z0ACYELmMBKvmpGB4T8hDUzIpiKTWAEj+e6mr2o0P+BTjRlKOFVjDSVahgkAaqUFHbq6tu0AAAAASUVORK5CYII=',
    'Cherty Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARklEQVR4nGNk+P+fAT9gZISrYUIRJQRgqiFKCWmAqYbYRchVSC4h6AFSAcK/yH4nwiU4DUR4nZBq1LAipBo1rIhwCdlhBQCwoxQPlzOfUgAAAABJRU5ErkJggg==',
    'Clay-Shale'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAJklEQVR4nGNk+M9APGDBKcOIVYwUs5lIUIvdPgjAZictXTIywgQAwXMHEViuCzsAAAAASUVORK5CYII=',
    'Coal-LigNite'                               : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAD0lEQVR4nGNgGAWjgDAAAAIoAAGcWSSWAAAAAElFTkSuQmCC',
    'Coarse Sand'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGP8z0ACYIGzGBkYGBgY/uPlMpFiNAMjSS6B2EDAAXAuC5rZ+K0izSWkhQlCNX5L/pPhEsrCBKsD4AAAqOIUE2T8pNYAAAAASUVORK5CYII=',
    'Coarse Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALUlEQVR4nGP8z0ACYIGzGBkYGBgY/uPlMpFiNAMjSS6B2EDAAXAuLV0yMsIEALtDDhMr0cX2AAAAAElFTkSuQmCC',
    'Diatomite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8z0ACYGJgYGBEFWJEItHFsZqNy0JGklxC2DxkcZb/cDdh04MmTppLhmmYoOkBAGgCEgoVn5w0AAAAAElFTkSuQmCC',
    'Dolomite'                                   : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAOUlEQVR4nGP8z4AdMDIwYEoxEa8Uu2pcSkkGjEQaA7EQu7uxKmUgRjX53kC4mxgzmEiyjokil+EHAM8cDA2YvqCzAAAAAElFTkSuQmCC',
    'Dolomitic Caly-Shale'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAP0lEQVR4nGNk+M+AAIwMKFwMwIJTKSMW1YxQFYRMhQAmKI1fKSMajQng+pGsZSRsKpICJnQ5XDYwMDCMlDABAMEnExG7n4N/AAAAAElFTkSuQmCC',
    'Dolomitic LimeStone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAM0lEQVR4nGNk+P+fAT9gZISrYSKgFBXQSDUjI9GqkZxOAkDSRIQBdA0TRkaiVZPnd1wAALR5DBNKlryqAAAAAElFTkSuQmCC',
    'Dolomitic Marl'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nLWQORIAMAgC14z//7Ip0nkwNqFUBMQI9vBxY+0sCml2O3vq4PfQnZUkQjZSEkmV2qtOUL965qFq+dQJABcAfg4P4mQE/gAAAABJRU5ErkJggg==',
    'Dolomitic Sandstone'                        : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nNWQwQoAIAhD3/r/f7ZDFDJM6NhOQ4c+pgABEABom1LKuxy1E8srquhN47gOwNJKo+wdr/9ueDKMnzppCnG8p04mYK4ZEWJIK0cAAAAASUVORK5CYII=',
    'Evaporite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAIUlEQVR4nGNgYGBgYGD4z8BADIOJSHUkKEKoHnXJIHYJAPYYO80JpAy3AAAAAElFTkSuQmCC',
    'Ferruginous Sandstone'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAWklEQVR4nJWPUQrAMAhDE9n9r+w+ZMFpF1goFFsTn0z8UADgc0p8d/Svq64+wUyLHdBTy5yjO22knLFf9xDhzW4vCoDfMFrgnD1g0pPkyQMg9loqOyQHt5G4byloER1pgAzNAAAAAElFTkSuQmCC',
    'Fine Sand'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALklEQVR4nGP8z8DAwMDAyMAAYeBnM8I5xAAmUhQzMDEicQiyaeoSIt3AMILCBAAkSggcF+UiNQAAAABJRU5ErkJggg==',
    'Fine Sandstone'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALklEQVR4nGP8z8DAwMDAyMAAYeBnM8I5xAAmUhQzMDEicQiyaeoSIt3AMILCBAAkSggcF+UiNQAAAABJRU5ErkJggg==',
    'Glauconitic Sandstone'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGP8z8DAwMDAyMAAYeAHTHCljDAhRiQ2A6ogI8lmM+BVimwPE5q9mFwURxJ0ALIjmTCtQwPIxo2MMAEAWdARI94gGbQAAAAASUVORK5CYII=',
    'Grainstone'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASUlEQVR4nK2QOQ4AIAzDUsT/v1yGLKGHAAmPYAULgzuOmFEbZ1V4s2fxqLJ3JjsZPfTUjtvlEg9ZJUJVEtL15roSiD/Yr1b2XxZ6YBYPaSFNqQAAAABJRU5ErkJggg==',
    'Granit'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATElEQVR4nI2RMQ4AIAgDwfjwPt3FodKi3uBQr4RoIjagk+E80RtKPmd721JGtLbmKHtbg/OpHpdLf4S769Y7bNs0Nv7sxwuG/uXdYxbP6RST+Z0ilQAAAABJRU5ErkJggg==',
    'Gypsiferous Clay-Shale'                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAP0lEQVR4nN2QwQ4AIAhCn/7/P9OlNiubnuMEcwLDEBiIicgTaJ0V5OPB2q4AvoVcVjlvNrQyPTb0OlGH+H6TAQy0I/SLHyq4AAAAAElFTkSuQmCC',
    'Gypsum'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARElEQVR4nNWQOw4AMAhCKSfn6B2aGP972dQnGA8AIUilY2KaLSgAesKjdUePNm4Jkacns5TJwjQLZsTWcirZ3jfp159cEkocGEBKwAkAAAAASUVORK5CYII=',
    'Halite'                                     : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAL0lEQVR4nGP8z0ACYMIvzYhVNSOmQjLMRgMsBFXArf3PwMD4H8MlePzNOBomGAAAhh8IGQlZVrQAAAAASUVORK5CYII=',
    'LimeStone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAKElEQVR4nGNk+P+fAT9gZISrYSKgFBUMHtWkAYR/kf1OHZcMHtWkAQCOZggPCrWWVQAAAABJRU5ErkJggg==',
    'Marl'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALklEQVR4nGNk+M9AADAywNUw4lTNiFWMoNlIgAm/YUTYBwHY7CTbJURYPzLCBACXSAoMolaWUgAAAABJRU5ErkJggg==',
    'Medium Sand'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nGP8zwAFjAwMDAwM//Gz4aqJAUxwgxmRLGFEUoEiRZLZDP+RGATZZLmbSMCI7B5cAQfn0s0luBxAZpgAAN9DFgfGmhrEAAAAAElFTkSuQmCC',
    'Medium Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAN0lEQVR4nGP8zwAFjAwMDAwMWLlwNiNcmhjABNHKiGQkI5I0OpdkswmaCmePDHdD9RMToySbDQCyZQ0hqQwZswAAAABJRU5ErkJggg==',
    'Metamorphic Rocks'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAZElEQVR4nI1QQQ7AMAiSpf//Mju4qYUumScroFCQjAgA1cRbOakCsGKvyUglyW7yUaQCpqbRiYkfdwKn+tbNiZ77NqYpk1okubaOHvw3HyeC/Up59O2aS9RyOjPIvBd4spqQvAHySX3yFrLg2wAAAABJRU5ErkJggg==',
    'Monogenic Breccia'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8z0AAMDIwwNUwoUlgKkUWZ8IlgRUw4ZFjxGAz/sdmJC7PMBL0JbEuwXTPyAgTACehCB65BHOLAAAAAElFTkSuQmCC',
    'Monom Conglomerate 2-4 mm'                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATklEQVR4nK2PMQ7AMAgDbdT/f9kZolStMLDkJgSHMBQGCADYWrwtFqoAnWnkVsPTj/VPQqVwDawMux+Vaj/x9pAk37VJqHMXn6LiUhLLAmDpFhDu5/5aAAAAAElFTkSuQmCC',
    'Monom Conglomerate 4-64 mm'                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARklEQVR4nGP8z0ACYIFQjDA+XDOmCFQ1I6qi/9hEIICJFIcwMP4nxSWMJPmSNJew4LIUq3sYGXB4nwFbyJAeJiS4hKQwAQBgDxUTE0sMfAAAAABJRU5ErkJggg==',
    'Mudstone'                                   : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nGNk+P+fgSBgZIQoYyKsFAlQqJqRETsbp9kQRRhKMQDEx5gkDLBgDxNkQSQ2ab5kJCq8sZtNyGekuYQ0AAAXgRQN+VTR2gAAAABJRU5ErkJggg==',
    'Nodular Limestone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nGNk+P+fAT9gZISrYYHy0QAOI1iQtWI1D1X1//+kmI1bjlKA5D4cbsVwCXZzsHgGh2ocAYVDNY6Awu0SygMKADvSHhlod/v/AAAAAElFTkSuQmCC',
    'Oolitic Limestone'                          : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATUlEQVR4nKWQQQoAIAgEd8X/f7kORaihQs0pY5k2iTEAgMRijRbyXGqY3flCnKPDpHPlQXeu6P1M9z//ppaq6JIqHfRuJxmmXtnkc1cTqxkgE5gMqmoAAAAASUVORK5CYII=',
    'Organic Shale'                              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAI0lEQVR4nGP8//8/AwMDIyMjAwMDfjYDAwMTAylgVPXwUQ0AB0MMFSP+cO0AAAAASUVORK5CYII=',
    'Packstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nJWQSQ4AIAgDwfj/L9cDB5HFhjmSAQoqgFBUTVtcdczsXSw1qoTVbECA29bi51lPWBxLmiokSU+yv+9/bXbZLMmMAzGhFgkmiHnkAAAAAElFTkSuQmCC',
    'Pelletic Limestone'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQElEQVR4nGNk+P+fAQ4YGaEMNEEYlwWrKAobCTBhCuEBpKlGcsn//9jdTTbA7TNs9iC5BMUQ7KbQKUyQAVXCBwC4JRwTwH80JgAAAABJRU5ErkJggg==',
    'Phosphatic Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nGNk+P+fAT9gZISrYUIRJQRgqiEGENIAUw1RSshVSC4h6AFSAZLtpLkEp4EIrxNSjRpWhFSjhhURLiE7rABaNhgP4X9LFwAAAABJRU5ErkJggg==',
    'Plastic Clay-Shale'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nJWQMQ4AIAgDqfH/X8ZJg0lbpRPDcSkgMlwQFZiW3QsN2rlBoJPBZXkVsE0g3YxOMfMmOnj8O64DPmi+qFJ0PfcC8DsNF7DOhSAAAAAASUVORK5CYII=',
    'Polym Conglomerate 2-4 mm'                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUklEQVR4nJWQSw6AMAgFB+L9r/xcaA2GT3VWpAwNPBMbDIBL8+fJGlWg1XWCVw5Ejrmt9yamtNyAdUY574NKuqS2O+oElYpb0wqVUGz+/si/BE8tkBEWwgrDvwAAAABJRU5ErkJggg==',
    'Polym Conglomerate 4-64 mm'                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASElEQVR4nJWQSQoAMAgDk+L/v5weitIVGhHccZSCITEMM67hMwOgzYXyCSiVW/e/UA4JrSs9kngtvfIQK6turTXg/8QgsX7SAf0bExKF9esDAAAAAElFTkSuQmCC',
    'Polymictic Breccia'                         : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGP8z0AAMDIwwNUwoUlgKkUWZ8IlgRUw4ZFjxGAz/sdmJC7PMBL0JbEuwXTPyAgTACehCB65BHOLAAAAAElFTkSuQmCC',
    'Quartzite'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nGP8zwAFjAwMcDYuwARRBweMSAxMNiNJZpMGsJuNi43T3VjZTAyoziWGTSxgxKoJp7uxhiuyW5HZLHgcR6m7AVtHExUWDGm0AAAAAElFTkSuQmCC',
    'Radiolarite'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nJXQWQoAIAgEUCe8/5XtQ4hcJnK+Eh4uwaQPRKy8wbQjzzGL4+C+NGKpDzfbu2alcWDw7l3Pp71/XNbvHTwq5Pw2sz/Z1scPFQSt+eAAAAAASUVORK5CYII=',
    'Reefal Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAU0lEQVR4nKWQQQrAIAwEJ8H/f3l7KESDiVI6x+COyxoSgBnBewnM4uLzqVQkM2NGI5N9K56+kw5ioHZ0vb+x5HbHNpTTUQ01Ll3zUL2bYqhj7588tSUuD6PAwGkAAAAASUVORK5CYII=',
    'Saliferous Clay-Shale'                      : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAN0lEQVR4nGNk+M9APGBhYGBgYGTAoocRi2pGhv8YErhtYyTJJdjsg9uA4UK8ZmO4kDSXjIwwAQDB7hILdBMh6QAAAABJRU5ErkJggg==',
    'Saliferous Sandstone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nLVOQQoAIAhz/v/Pdih0aSBBDRFxYxtMFiABoxsi5puJFsrGbO+f7dl6g4pp5VKIJ+B974N6wsqdkkMNmlQ69sfed94D0X0NImOsELkAAAAASUVORK5CYII=',
    'Sandy Clay-Shale'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAL0lEQVR4nGNk+M9APGBBMBkZUHQyYlHNSJLZTCSoxW4fBPxHUvIfzqSdS0ZGmAAABcoLEUm6bjkAAAAASUVORK5CYII=',
    'Sandy Dolomite'                             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nK2Q0QoAMAgCdf//z+1tQd1gxHwsOVSHWJb6a52fyVrvHYDUiYDNPiluudH6xJ7XSPYLI3PjlKWM4+PARRsMxQ8PGOp1HwAAAABJRU5ErkJggg==',
    'Sandy Limestone'                            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQklEQVR4nGNk+P+fAT9gZISrYSKgFBWgqmZkZGBkxKOaBYVHyFWkuYQ0gPAvst+p4xLcqrGFDwtWlQwM2MOHlmECAJZUDBefEMWaAAAAAElFTkSuQmCC',
    'Sandy and calcareous Clay-Shale'            : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANElEQVR4nGNk+M9APGBBMBkZGBgYEJoZsahmJMlsJsJKkCxhwWojipOQAAu1XYJk3MgIEwB9KAogMX8ppwAAAABJRU5ErkJggg==',
    'Sandy and calcareous Dolomite'              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAASklEQVR4nK1QQQ4AIAhC//9nO7hZQ6214igMATHUECBT6oQsoiwNgZCBX7uHd2DvVgeY56ZwOVjUOHg/1Zje5cAELQfGtsangQkDtU8OEjwAEb4AAAAASUVORK5CYII=',
    'Sandy and dolomitic Clay-Shale'             : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAARUlEQVR4nK2QQQoAIAzDUvH/X54ncYLKCva0y9oQEfgJ1lu+96jaLQiaRaAX217skACYJGn3pxNAdRJB0K9WTps1kmlwAPkbEwRrX37hAAAAAElFTkSuQmCC',
    'Sandy and dolomitic Limestone'              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQUlEQVR4nGNk+P+fAT9gZISrYSKgFBWgqmZkZGBkxKOaBYVHyFWkuYQ0gPAvst+R5FEE8boEQz9e1RhWURLe1AUAVMIQETu29e4AAAAASUVORK5CYII=',
    'Sandy, calcareous and dolomitic Clay-Shale' : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMUlEQVR4nGNk+M9AADAywNUwIlQjiUK5WDQSNBsJMOE3DNNROAA2F5LtEiKsHxlhAgDbkA4MbSio3wAAAABJRU5ErkJggg==',
    'Shelly Limestone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAR0lEQVR4nKWQSQ4AIAgDC+H/X8aLETQWjc55WFqBO2pEhqMHdUb7dN7EMQBwD6l8zG6kRyJvzs546IQeXrsyqmLTVWnjr6sGwxsUFwL9UYIAAAAASUVORK5CYII=',
    'Shelly Sandstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAL0lEQVR4nGP8z0AK+A8j/yNxcTEYIRxGVAlcgJEclyA7Bo/z8JmN6TyyXDLMwwQAVEUn5dyYZycAAAAASUVORK5CYII=',
    'Shelly Siltstone'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAATklEQVR4nKWRSQ4AIAgDB///Z7yh1D32YIwlzVDNeVABDOIUiWU+2J4vu2wHy6O9q9kHbiWb4q64RYF3Na0k5O7GNj+2vIlsj32vq58KVdIZDiJU/WEjAAAAAElFTkSuQmCC',
    'Silicified Claystone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAK0lEQVR4nGNk+M9APGDBKcOIVYwUs5mgZsBNQuMStg8CsNlJqktIASMjTADJrwcZZSLwFgAAAABJRU5ErkJggg==',
    'Silicified Limestone'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAANklEQVR4nGNk+P+fAT9gZISrYSKgFBXQQzUjI04GHGCK4AcI/yL7nZBLiAO0VY3H73jChxgAAJtOCB+XiwIpAAAAAElFTkSuQmCC',
    'Silt'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALklEQVR4nGP4z8DAwMDwH4YYkEhMEUYIi0jABKEYkUg8IqSbTdBIBDnqbgrdDQA+eBAaMK21ZAAAAABJRU5ErkJggg==',
    'Siltstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAL0lEQVR4nGP8z4AAjAwM/2EkAzZxRjQJ/ICJEaYbDWAVJ9FsguYhi4+6G1OcNLMB5r8KIK4wHFcAAAAASUVORK5CYII=',
    'Silty Clay-Shale'                           : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAALUlEQVR4nGNk+M9APGCB0owMUG3IDAzASJLZTCSoxQf+w5z0H8GlpUtGRpgAAEJhEwel2CwqAAAAAElFTkSuQmCC',
    'Silty Marl'                                 : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMElEQVR4nGNk+M9AADAyIKn5D+NgMrBoJGg2EmBCsZF8gOwwGJdsl+ACKC4cCWECAFFIG/TvFDT2AAAAAElFTkSuQmCC',
    'Silty dolomitic Marl'                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAUElEQVR4nJ2QSQ7AMAgDx1X+/2V6SdSEJULlAhY2BoTRjzGzmLK9KNnRIfN8DqSc1AhbSvugusME5ja5UoOjKxJVbNS3Ds/j31uyDds/AeAF/kAdAP0L+PQAAAAASUVORK5CYII=',
    'Silty, calcareous and dolomitic Clay-Shale' : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAMElEQVR4nGNk+M9AADAyIKn5D+NgMrBoJGg2EmBCsZF8gOwwGJdsl+ACKC4cCWECAFFIG/TvFDT2AAAAAElFTkSuQmCC',
    'Slaty Shale'                                : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAFklEQVR4nGNgIAUwMvwnSf2o2cPFbABujgYBlSHfbwAAAABJRU5ErkJggg==',
    'Sylvite'                                    : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAO0lEQVR4nGNsYMAOMMUbGBhYcEmgiUPYLJgmNWAw4ACLalwiDAwMjFhFcQEmUhSTqJoFl0QDNpGhGoIAAZsMpDuBJngAAAAASUVORK5CYII=',
    'Void'                                       : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAF0lEQVR4nGP8//8/A9GAiXilo6qHlWoAh/ADFdofhqIAAAAASUVORK5CYII=',
    'Volcanic Rock'                              : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAXUlEQVR4nH1QwQ0AMQjCTsbojnYPL4YorZ9KCoJGZgIgCaD6gt1rRT37b+h/9sDbRGFoEmuiGp/E5iY5k7wF5+Hb8TybpI7cgrD3vkU6jcfVutTBb3mzmls2z275AT0VUFEc1K2XAAAAAElFTkSuQmCC',
    'Wackstone'                                  : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAMCAIAAAAyIHCzAAAAQ0lEQVR4nGNk+P+fgSBgZIQoYyKsFAlQqJqRETubDLNRAcTHmCTcMvQwgdj+/z+CQcAl2EzFYTZegGo2RiDgVU1dAABPyBgGdo0uhQAAAABJRU5ErkJggg==',
}

PATTERN_IDS: typing.Dict[str, str] = {
    'Anhydrite'                                  : 'FillPattern95',
    'Anhydritic Clay-Shale'                      : 'FillPattern53',
    'Anhydritic Limestone'                       : 'FillPattern19',
    'Anhydritic Sandstone'                       : 'FillPattern81',
    'Anhydritic Siltsone'                        : 'FillPattern82',
    'Argillaceous Dolomite'                      : 'FillPattern29',
    'Argillaceous Limestone'                     : 'FillPattern5',
    'Argillaceous Sandstone'                     : 'FillPattern68',
    'Argillaceous Siltstone'                     : 'FillPattern67',
    'Argillaceous and Sandy Dolomite'            : 'FillPattern33',
    'Argillaceous and calcareous Dolomite'       : 'FillPattern31',
    'Argillaceous and calcareous Sandstone'      : 'FillPattern72',
    'Argillaceous and dolomitic Limestone'       : 'FillPattern7',
    'Argillaceous and dolomitic Sandstone'       : 'FillPattern73',
    'Argillaceous and sandy Limestone'           : 'FillPattern8',
    'Arkosic Sandstone'                          : 'FillPattern74',
    'Basalt'                                     : 'FillPattern99',
    'Bedded Chert'                               : 'FillPattern80',
    'Bioclastic Limestone'                       : 'FillPattern16',
    'Bituminous Clay-Shale'                      : 'FillPattern56',
    'Bituminous Limestone'                       : 'FillPattern21',
    'Bituminous Sandstone'                       : 'FillPattern84',
    'Bundstone'                                  : 'FillPattern26',
    'Calacareous Dolomite'                       : 'FillPattern28',
    'Calcareous Clay-Shale'                      : 'FillPattern38',
    'Calcareous Sandstone'                       : 'FillPattern69',
    'Calcareous and dolomitic Clay-Shale'        : 'FillPattern42',
    'Calcareous and dolomitic Sandstone'         : 'FillPattern71',
    'Cargneule'                                  : 'FillPattern34',
    'Chalk'                                      : 'FillPattern10',
    'Chert'                                      : 'FillPattern79',
    'Cherty Limestone'                           : 'FillPattern18',
    'Clay-Shale'                                 : 'FillPattern35',
    'Coal-LigNite'                               : 'FillPattern2',
    'Coarse Sand'                                : 'FillPattern61',
    'Coarse Sandstone'                           : 'FillPattern65',
    'Diatomite'                                  : 'FillPattern77',
    'Dolomite'                                   : 'FillPattern27',
    'Dolomitic Caly-Shale'                       : 'FillPattern39',
    'Dolomitic LimeStone'                        : 'FillPattern4',
    'Dolomitic Marl'                             : 'FillPattern49',
    'Dolomitic Sandstone'                        : 'FillPattern70',
    'Evaporite'                                  : 'FillPattern93',
    'Ferruginous Sandstone'                      : 'FillPattern86',
    'Fine Sand'                                  : 'FillPattern59',
    'Fine Sandstone'                             : 'FillPattern63',
    'Glauconitic Sandstone'                      : 'FillPattern85',
    'Grainstone'                                 : 'FillPattern25',
    'Granit'                                     : 'FillPattern100',
    'Gypsiferous Clay-Shale'                     : 'FillPattern55',
    'Gypsum'                                     : 'FillPattern96',
    'Halite'                                     : 'FillPattern94',
    'LimeStone'                                  : 'FillPattern3',
    'Marl'                                       : 'FillPattern48',
    'Medium Sand'                                : 'FillPattern60',
    'Medium Sandstone'                           : 'FillPattern64',
    'Metamorphic Rocks'                          : 'FillPattern101',
    'Monogenic Breccia'                          : 'FillPattern91',
    'Monom Conglomerate 2-4 mm'                  : 'FillPattern89',
    'Monom Conglomerate 4-64 mm'                 : 'FillPattern87',
    'Mudstone'                                   : 'FillPattern22',
    'Nodular Limestone'                          : 'FillPattern13',
    'Oolitic Limestone'                          : 'FillPattern11',
    'Organic Shale'                              : 'FillPattern57',
    'Packstone'                                  : 'FillPattern24',
    'Pelletic Limestone'                         : 'FillPattern12',
    'Phosphatic Limestone'                       : 'FillPattern20',
    'Plastic Clay-Shale'                         : 'FillPattern37',
    'Polym Conglomerate 2-4 mm'                  : 'FillPattern90',
    'Polym Conglomerate 4-64 mm'                 : 'FillPattern88',
    'Polymictic Breccia'                         : 'FillPattern92',
    'Quartzite'                                  : 'FillPattern66',
    'Radiolarite'                                : 'FillPattern78',
    'Reefal Limestone'                           : 'FillPattern15',
    'Saliferous Clay-Shale'                      : 'FillPattern54',
    'Saliferous Sandstone'                       : 'FillPattern83',
    'Sandy Clay-Shale'                           : 'FillPattern40',
    'Sandy Dolomite'                             : 'FillPattern30',
    'Sandy Limestone'                            : 'FillPattern6',
    'Sandy and calcareous Clay-Shale'            : 'FillPattern43',
    'Sandy and calcareous Dolomite'              : 'FillPattern32',
    'Sandy and dolomitic Clay-Shale'             : 'FillPattern44',
    'Sandy and dolomitic Limestone'              : 'FillPattern9',
    'Sandy, calcareous and dolomitic Clay-Shale' : 'FillPattern46',
    'Shelly Limestone'                           : 'FillPattern14',
    'Shelly Sandstone'                           : 'FillPattern75',
    'Shelly Siltstone'                           : 'FillPattern76',
    'Silicified Claystone'                       : 'FillPattern52',
    'Silicified Limestone'                       : 'FillPattern17',
    'Silt'                                       : 'FillPattern58',
    'Siltstone'                                  : 'FillPattern62',
    'Silty Clay-Shale'                           : 'FillPattern41',
    'Silty Marl'                                 : 'FillPattern50',
    'Silty dolomitic Marl'                       : 'FillPattern51',
    'Silty, calcareous and dolomitic Clay-Shale' : 'FillPattern47',
    'Slaty Shale'                                : 'FillPattern36',
    'Sylvite'                                    : 'FillPattern97',
    'Void'                                       : 'FillPattern1',
    'Volcanic Rock'                              : 'FillPattern98',
    'Wackstone'                                  : 'FillPattern23',
}

assert AREA_DATA_URI_SCHEME_MONO.keys() == AREA_DATA_URI_SCHEME_RGB.keys() == PATTERN_IDS.keys()

AREA_KEYS = AREA_DATA_URI_SCHEME_MONO.keys()


def write_svg_defs(xS, area_map, keys=None):
    if keys is None:
        keys = AREA_KEYS
    with XmlWrite.Element(xS, 'defs'):
        for pattern in keys:
            attrs_pattern = {
                'id': PATTERN_IDS[pattern],
                'width': '15',
                'height': '12',
                # 'viewBox' : "0 0 15 12",
                'patternUnits' : 'userSpaceOnUse',
                'alt': pattern,
            }
            with XmlWrite.Element(xS, 'pattern', attrs_pattern):
                attrs_image = {
                    'href': area_map[pattern],
                }
                with XmlWrite.Element(xS, 'image', attrs_image):
                    pass
