<?xml version="1.0" encoding="UTF-8"?>
<!--
Copyright (C) 2008-2010 Martin Riesz <riesz.martin at gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
-->
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">

<document>
    <subnet>
        <id>0</id>
        <x>0</x>
        <y>0</y>
        <xsl:for-each select="pnml/net/place">
            <place>
                <id><xsl:value-of select="@id"/></id>
                <x><xsl:value-of select="graphics/position/@x"/></x>
                <y><xsl:value-of select="graphics/position/@y"/></y>
                <label><xsl:value-of select="name/value"/></label>
                <tokens><xsl:value-of select="initialMarking/token/value"/><xsl:value-of select="initialMarking/value"/></tokens>
                <isStatic>false</isStatic>
                <type><xsl:value-of select="type"/></type>
            </place>
        </xsl:for-each>
        <xsl:for-each select="pnml/net/transition">
            <transition>
                <id><xsl:value-of select="@id"/></id>
                <x><xsl:value-of select="graphics/position/@x"/></x>
                <y><xsl:value-of select="graphics/position/@y"/></y>
                <label><xsl:value-of select="name/value"/></label>
                <timed><xsl:value-of select="timed"/></timed>
                <rate><xsl:value-of select="rate"/></rate>
                <automatic><xsl:value-of select="automatic"/></automatic>
                <informed><xsl:value-of select="informed"/></informed>
                <enableWhenTrue><xsl:value-of select="enableWhenTrue"/></enableWhenTrue>
                <guard><xsl:value-of select="guard"/></guard>
                <cost><xsl:value-of select="cost"/></cost>
                <distribution><xsl:value-of select="stochasticProperties/@distribution"/></distribution>
                <var1><xsl:value-of select="stochasticProperties/@var1"/></var1>
                <var2><xsl:value-of select="stochasticProperties/@var2"/></var2>
                <labelVar1><xsl:value-of select="stochasticProperties/@labelVar1"/></labelVar1>
                <labelVar2><xsl:value-of select="stochasticProperties/@labelVar2"/></labelVar2>
            </transition>
        </xsl:for-each>
        <xsl:for-each select="pnml/net/arc">
            <arc>
                <type><xsl:value-of select="type"/></type>
                <sourceId><xsl:value-of select="@source"/></sourceId>
                <destinationId><xsl:value-of select="@target"/></destinationId>
                <multiplicity>
                    <xsl:choose>
                        <xsl:when test="inscription/value &gt; 0">
                            <xsl:value-of select="inscription/value"/>
                        </xsl:when>
                        <xsl:otherwise>
                            1
                        </xsl:otherwise>
                    </xsl:choose>
                </multiplicity>
                <xsl:for-each select="graphics/position">
                    <breakPoint>
                        <x><xsl:value-of select="@x"/></x>
                        <y><xsl:value-of select="@y"/></y>
                    </breakPoint>
                </xsl:for-each>
            </arc>
        </xsl:for-each>
    </subnet>
</document>

</xsl:template>
</xsl:transform>
