{% load static %}
{% load pipeline %}
{% load api_url %}
title: Changelog
page_image: img/og_image/tools.png
meta_description: CAP Data/Feature Change Log
explainer: If our data or user-facing research features change in significant ways&mdash;beyond bug fixes and minor changes&mdash;we'll record those changes here.
top_section_style: bg-black
row_style: bg-tan
extra_head: {% stylesheet 'docs' %}

# July 31, 2019

**Website:**

* Improved case display at cite.case.law:
    * Cases include images for non-textual regions (figures and illustrations)
        ([example](https://cite.case.law/f2d/537/531/))
    * Case text includes italics, where detected by OCR
    * Case text includes pin cites, i.e. page breaks that can be linked to 
        ([example](https://cite.case.law/f2d/537/531/#p533))
        
**API:**

* Removed from `/cases/` endpoint:
    * In full case responses with JSON format, `["casebody"]["data"]["parties"]` is no longer included.
      The `["name"]` attribute provides the same information in a cleaner format.
    * Queries for CaseXML documents (`/cases/<id>/?full_case=true&format=xml`) will return only `<casebody>`, 
      and not the entire CaseXML file. The outer wrapper had no useful information other than to estimate the 
      location of page breaks, which are now precisely marked by `<page-number>` elements.
          
**Data format:**

* Added to case HTML and XML:
    * `<img>` tags to show images for non-textual regions (figures and illustrations)
    * `<em>` tags to show italics detected by OCR
    * `<page-number>` (in xml) or `<a class="page-number">` (in html) tags to mark page breaks
* Removed from case XML:
    * The `pgmap` attribute was removed. It was confusing, because it referred to the page-side index in the 
        physical volume rather than to the printed page label, and it did not allow for precise placement of
        page breaks within a paragraph. The replacement is to use `<page-number>` elements to infer the correct
        page number for each element.
          
# June 19, 2019

**Website:**

* Started recording this public changelog.
* Added the [historic trends]({% url 'trends' %}) tool.

**API:**

* Added the [ngrams]({% api_url "ngrams-list" %}) endpoint. Here are the [docs]({% url 'api' %}#endpoint-ngrams).
