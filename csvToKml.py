# -*- coding: utf-8 -*-
import pandas as pd
import os


def getKML(inputFile):
    print(inputFile)
    htmlColors = ['6fb7b7', 'e1e100', '004b97', 'ffe153', '600030', 'ffdc35', '84c1ff', 'caffff', '00bb00', 'ffa042',
                  '8f4586', '000079', 'fff4c1', '9f35ff', 'ff0080', '97cbff', 'ffffce', '408080', 'ffecec', 'b766ad',
                  '7b7b7b', 'ffc78e', '737300', '2f0000', '642100', '005757', 'ad5a5a', '0066cc', 'cf9e9e', '01814a',
                  '804040', 'ff44ff', 'ae00ae', 'ff8000', '0000e3', 'ff00ff', 'b8b8dc', 'ffdcb9', '28ff28', 'a6ffa6',
                  'c2c287', 'e8e8d0', '949449', 'ebd3e8', 'c7c7e2', 'c1ffe4', 'ff8eff', 'fcfcfc', '01b468', '921aff',
                  'f0fff0', '4d0000', 'ffdac8', '9f4d95', 'f3f3fa', '5e005e', 'fffaf4', 'e0e0e0', 'ffe6d9', '53ff53',
                  '006000', 'ff359a', 'fffff4', '7afec6', 'ff2d2d', '4a4aff', '009393', 'ea7500', 'dfffdf', 'c4c400',
                  'efffd7', 'a6a6d2', 'ffeedd', 'fffcec', '424200', 'fff0ac', '743a3a', 'acd6ff', '5b5b00', 'e8ffc4',
                  '9d9d9d', 'd2e9ff', 'c6a300', '82d900', 'f2e6e6', 'ff5151', 'eac100', 'ca8eff', '0080ff', '00aeae',
                  'e1c4c4', '5b5b5b', '5b00ae', 'ae8f00', 'ffd0ff', 'ffd306', 'ceceff', 'ffff93', '4dffff', '0072e3',
                  'ecffff', 'ff9d6f', '820041', 'ffaad5', '930000', '005ab5', '600000', '613030', '93ff93', '8c8c00',
                  'ffbd9d', 'd8d8eb', 'ffb5b5', 'fbfffd', 'ffe66f', 'ae57a4', '009100', '80ffff', 'c4e1ff', '007979',
                  'd0d0d0', '3a006f', '930093', '46a3ff', 'e800e8', '467500', 'fff8d7', 'faf4ff', '7d7dff', 'ffc1e0',
                  'ffad86', '484891', '000079', 'ecf5ff', 'b7ff4a', 'd200d2', 'ff5809', '00e3e3', '8e8e8e', '707038',
                  'ff60af', 'f9f900', 'ffffdf', '9f5000', 'ffe6ff', 'bf0060', 'ff0000', 'ff7575', '73bf00', '5b4b00',
                  'e6e6f2', '0000c6', '02c874', 'ececff', '7e3d76', '460046', 'fff3ee', 'a6a600', '019858', 'd7ffee',
                  '616130', 'fbfbff', 'c48888', 'd3ff93', 'd6d6ad', 'afaf61', 'bb3d00', 'ffed97', '003d79', 'ce0000',
                  'd9b300', 'ebd6d6', '3c3c3c', '9393ff', 'f00078', '003e3e', 'ff8f59', '6f00d2', '336666', 'b87070',
                  'bbffff', '844200', '00ffff', '2828ff', 'ffd2d2', '984b4b', '4f4f4f', 'ffbfff', 'aaaaff', 'dcb5ff',
                  'f1e1ff', 'ff9224', 'ffbb77', 'ffcbb3', 'fff7ff', '8600ff', '4efeb3', '6a6aff', 'ea0000', '66b3ff',
                  'ffecf5', 'dab1d5', 'ffa6ff', 'a6ffff', 'deffac', 'dedebe', 'f75000', '02df82', 'ffff6f', 'ffffb9',
                  'cdcd9a', 'ffffaa', 'adfedc', 'ffe4ca', 'bebebe', '9f0050', '9aff02', '00caca', 'ff77ff', '4b0091',
                  'ff8040', 'fdffff', '750000', '0000c6', '3d7878', 'ccff80', '1afd9c', '6c3365', '5151a2', 'a23400',
                  '02f78e', 'c2ff68', 'c4e1e1', '007500', 'c07ab8', '5cadad', 'ae0000', 'f0f0f0', '95caca', '2894ff',
                  '6c6c6c', 'd2a2cc', 'a5a552', 'd26900', 'ca8ec2', 'e6caff', '28004d', 'b3d9d9', 'b15bff', '64a600',
                  'a8ff24', '00db00', 'be77ff', 'ffaf60', '750075', 'ffff37', '9999cc', '7373b9', '81c0c0', 'f5ffe8',
                  'ff9797', 'd1e9e9', '977c00', 'bbffbb', 'ff79bc', '00ec00', 'ceffce', '4f9d9d', '8cea00', '79ff79',
                  'b9b973', 'd9ffff', '000093', 'ffd9ec', '808040', 'a3d1d1', '8080c0', 'bb5e00', '5a5aad', 'd94600',
                  'd9b3b3', 'ff95ca', 'b9b9ff', 'fff7fb', '272727', 'ffd1a4', 'e2c2de', 'adadad', 'ddddff', '00a600',
                  'd3a4ff', '796400', '96fed1', 'd9006c', '842b00', '006030', '548c00', 'e8fff5']
    cnt = len(htmlColors)

    df = pd.read_csv(inputFile)[["cust_code", "lng", "lat", "cluster_id"]]
    groups = sorted(list(set(df["cluster_id"].values)))
    savePath = "C:\\Users\\fengsy\\Desktop\\%s.kml" % inputFile.split(".")[0]
    try:
        os.remove(savePath)
    except:
        pass
    with open(savePath, 'a') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://earth.google.com/kml/2.0">\n<Document>\n')
        # 写入图标类型及其颜色
        for i in range(len(groups)):
            j = str(i - 1) if i > 0 else ""
            normalStyle = ('<Style id="s_ylw-pushpin%s">\n'
                           '<IconStyle>\n'
                           '<color>ff%s</color>\n'
                           '<scale>0.9</scale>\n'
                           '<Icon>\n'
                           '<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>\n'
                           '</Icon>\n'
                           '</IconStyle>\n'
                           '<LabelStyle>\n'
                           '<color>00ffffff</color>\n'
                           '</LabelStyle>\n'
                           '<ListStyle></ListStyle>\n'
                           '</Style>\n') % (j, htmlColors[i % cnt])
            highlightStyle = ('<Style id="s_ylw-pushpin_hl%s">\n'
                              '<IconStyle>\n'
                              '<color>ff%s</color>\n'
                              '<scale>0.590909</scale>\n'
                              '<Icon>\n'
                              '<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n'
                              '</Icon>\n'
                              '</IconStyle>\n'
                              '<LabelStyle>\n'
                              '<color>00ffffff</color>\n'
                              '</LabelStyle>\n'
                              '<ListStyle></ListStyle>\n'
                              '</Style>\n') % (j, htmlColors[i % cnt])
            styleMap = ('<StyleMap id="m_ylw-pushpin%s">\n'
                        '<Pair>\n'
                        '<key>normal</key>\n'
                        '<styleUrl>#s_ylw-pushpin%s</styleUrl>\n'
                        '</Pair>\n'
                        '<Pair>\n'
                        '<key>highlight</key>\n'
                        '<styleUrl>#s_ylw-pushpin_hl%s</styleUrl>\n'
                        '</Pair>\n'
                        '</StyleMap>\n') % (j, j, j)
            f.write(normalStyle)
            f.write(highlightStyle)
            f.write(styleMap)
        # 写入点坐标
        for i, group in enumerate(groups):
            segDf = df[df["cluster_id"] == group]
            f.write('<Folder>\n')
            f.write("<name>" + str(group) + "</name>\n")
            j = str(i - 1) if i > 0 else ""
            for row in segDf.values:
                custCode, lng, lat = row[0], row[1], row[2]
                f.write('<Placemark>\n')
                f.write("<name>" + str(int(custCode)) + "</name>\n")
                f.write('<styleUrl>#m_ylw-pushpin%s</styleUrl>\n' % j)
                f.write("<Point><coordinates>" + str(lng) + "," + str(lat) + ",0</coordinates></Point>\n")
                f.write('</Placemark>\n')
            f.write('</Folder>\n')
        f.write('</Document>\n</kml>\n')