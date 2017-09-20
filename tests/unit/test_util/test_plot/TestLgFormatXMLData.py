#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2012 Paul Ross
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
"""Tests ...

Created on Jan 31, 2012

@author: paulross
"""

__author__  = 'Paul Ross'
__date__    = '2012-01-31'
__version__ = '0.1.0'
__rights__  = 'Copyright (c) 2012 Paul Ross.'

LGFORMAT_HDT = """<LgFormat UniqueId="HDT" xmlns="x-schema:LgSchema2.xml">
  <Description>High Definition Dipmeter</Description>
  <LgVerticalScale UniqueId="VerticalScale">
    <IndexScaler>100</IndexScaler>
    <IndexUnit>FT</IndexUnit>
    <PaperScaler>5</PaperScaler>
    <PaperUnit>LG_PAPER_INCH</PaperUnit>
  </LgVerticalScale>
  <LgFont UniqueId="minorFont">
    <Bold>0</Bold>
    <Name>Courier New</Name>
    <Size>8</Size>
  </LgFont>
  <LgFont UniqueId="majorFont">
    <Bold>1</Bold>
    <Name>Courier New</Name>
    <Size>11</Size>
  </LgFont>
  <LgIndexGrid UniqueId="indexGrid">
    <LgIndexLine UniqueId="unitLine">
      <Color>818181</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <Spacing>2</Spacing>
      <SpacingUnit>Ft</SpacingUnit>
      <Thickness>1</Thickness>
    </LgIndexLine>
    <LgIndexLine UniqueId="minorLine">
      <Color>898989</Color>
      <Spacing>10</Spacing>
      <SpacingUnit>Ft</SpacingUnit>
      <Thickness>1.5</Thickness>
      <LgIndexNumber UniqueId="minorNumberInDepthTrack">
        <Font>minorFont</Font>
      </LgIndexNumber>
    </LgIndexLine>
    <LgIndexLine UniqueId="majorLine">
      <Color>000000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <Spacing>50</Spacing>
      <SpacingUnit>Ft</SpacingUnit>
      <Thickness>2</Thickness>
      <LgIndexNumber UniqueId="majorNumberInDepthTrack">
        <Font>majorFont</Font>
      </LgIndexNumber>
    </LgIndexLine>
  </LgIndexGrid>
  <LgTrack UniqueId="track1">
    <BackgroundColor>FFFFFF</BackgroundColor>
    <Description>Track 1</Description>
    <LeftPosition>0</LeftPosition>
    <RightPosition>2.4</RightPosition>
    <LgLinearGrid UniqueId="minorGrid1">
      <Color>818181</Color>
      <LineCount>11</LineCount>
    </LgLinearGrid>
    <LgLinearGrid UniqueId="majorGrid11">
      <Color>818181</Color>
      <LineCount>3</LineCount>
      <Thickness>2</Thickness>
    </LgLinearGrid>
    <LgCurve UniqueId="GammaRay">
      <ChannelName>GR</ChannelName>
      <Color>00C000</Color>
      <LeftLimit>0</LeftLimit>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>150</RightLimit>
      <Thickness>1.75</Thickness>
      <WrapMode>LG_WRAPPED</WrapMode>
      <WrapCount>1</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="C1Caliper">
      <ChannelName>C1</ChannelName>
      <Color>FF0000</Color>
      <LeftLimit>6</LeftLimit>
      <LineStyle>LG_DASH_LINE</LineStyle>
      <RightLimit>16</RightLimit>
      <Thickness>1.75</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="C2Caliper">
      <ChannelName>C2</ChannelName>
      <Color>0000FF</Color>
      <LeftLimit>6</LeftLimit>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>16</RightLimit>
      <Thickness>1.75</Thickness>
      <WrapCount>1</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="HoleAzimuth">
      <ChannelName>HAZI</ChannelName>
      <Color>898989</Color>
      <LeftLimit>-40</LeftLimit>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>360</RightLimit>
      <Thickness>1.75</Thickness>
      <WrapCount>0</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="Pad1Azimuth">
      <ChannelName>P1AZ</ChannelName>
      <LeftLimit>-40</LeftLimit>
      <Color>008000</Color>
      <LineStyle>LG_DOT_LINE</LineStyle>
      <RightLimit>360</RightLimit>
      <Thickness>1.75</Thickness>
      <Visible>1</Visible>
      <WrapCount>0</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="RelativeBearing">
      <ChannelName>RB</ChannelName>
      <LeftLimit>-40</LeftLimit>
      <Color>008000</Color>
      <LineStyle>LG_DOT_LINE</LineStyle>
      <RightLimit>360</RightLimit>
      <Thickness>1.75</Thickness>
      <Visible>1</Visible>
      <WrapCount>0</WrapCount>
    </LgCurve>
    <LgCurve UniqueId="Deviation">
      <ChannelName>DEVI</ChannelName>
      <LeftLimit>-5</LeftLimit>
      <Color>008000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>45</RightLimit>
      <Thickness>1.75</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
  </LgTrack>
  <LgTrack UniqueId="DepthTrack">
    <BackgroundColor>0FFFFF</BackgroundColor>
    <Description>Depth Track</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <IndexNumbersVisible>1</IndexNumbersVisible>
    <LeftPosition>2.4</LeftPosition>
    <RightPosition>3.2</RightPosition>
  </LgTrack>
  <LgTrack UniqueId="track2">
    <Description>Track 2</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>3.2</LeftPosition>
    <RightPosition>5.6</RightPosition>
  </LgTrack>
  <LgTrack UniqueId="track3">
    <Description>Track 2</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>5.6</LeftPosition>
    <RightPosition>8</RightPosition>
  </LgTrack>
  <LgTrack UniqueId="TrackFC0">
    <BackgroundColor>0FFFFF</BackgroundColor>
    <Description>Track FC1</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>3.2</LeftPosition>
    <RightPosition>4.2</RightPosition>
    <LgCurve UniqueId="FC0">
      <ChannelName>FC0</ChannelName>
      <LeftLimit>0</LeftLimit>
      <Color>ff0000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>256</RightLimit>
      <Thickness>0.5</Thickness>
      <Visible>1</Visible>
      <WrapCount>0</WrapCount>
    </LgCurve>
  </LgTrack>
  <LgTrack UniqueId="TrackFC1">
    <BackgroundColor>0FFFFF</BackgroundColor>
    <Description>Track FC1</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>3.2</LeftPosition>
    <RightPosition>4.2</RightPosition>
    <LgCurve UniqueId="FC1">
      <ChannelName>FC1</ChannelName>
      <LeftLimit>0</LeftLimit>
      <Color>000000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>256</RightLimit>
      <Thickness>0.5</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
  </LgTrack>
  <LgTrack UniqueId="TrackFC2">
    <Description>Track FC2</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>4.4</LeftPosition>
    <RightPosition>5.4</RightPosition>
    <LgCurve UniqueId="FC2">
      <ChannelName>FC2</ChannelName>
      <LeftLimit>0</LeftLimit>
      <Color>000000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>256</RightLimit>
      <Thickness>0.5</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
  </LgTrack>
  <LgTrack UniqueId="TrackFC3">
    <Description>Track FC3</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>5.6</LeftPosition>
    <RightPosition>6.6</RightPosition>
    <LgCurve UniqueId="FC3">
      <ChannelName>FC3</ChannelName>
      <LeftLimit>0</LeftLimit>
      <Color>000000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>256</RightLimit>
      <Thickness>0.5</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
  </LgTrack>
  <LgTrack UniqueId="TrackFC4">
    <Description>Track FC4</Description>
    <IndexLinesVisible>0</IndexLinesVisible>
    <LeftPosition>6.8</LeftPosition>
    <RightPosition>7.8</RightPosition>
    <LgCurve UniqueId="FC4">
      <ChannelName>FC4</ChannelName>
      <LeftLimit>0</LeftLimit>
      <Color>000000</Color>
      <LineStyle>LG_SOLID_LINE</LineStyle>
      <RightLimit>256</RightLimit>
      <Thickness>0.5</Thickness>
      <Visible>1</Visible>
      <WrapCount>1</WrapCount>
    </LgCurve>
  </LgTrack>
</LgFormat>
"""
