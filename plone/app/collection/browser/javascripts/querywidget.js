;(function($) {

    // Define querywidget namespace if it doesn't exist
    if (typeof($.querywidget) == "undefined") {
        $.querywidget = {
            config: {},
            initialized: false
        };
    }

    // Create a select menu
    $.querywidget.createSelect = function (values, selectedvalue, className, name) {

        // Create select
        var select = $(document.createElement('select'))
                            .addClass(className)
                            .attr('name', name);
        $.each(values, function (i, val) {
            var option = $(document.createElement('option'))
                            .attr('value', i)
                            .html(val.title);
            if (i == selectedvalue) {
                option.attr('selected', 'selected');
            }
            if (typeof(val.group) != "undefined") {
                var optgroup = select.find("optgroup[label=" + val.group + "]");
                if (optgroup.length == 0) {
                    optgroup = $(document.createElement('optgroup'))
                                .attr('label', val.group);
                    optgroup.append(option);
                    select.append(optgroup);
                } else {
                    optgroup.append(option);
                }
            } else {
                select.append(option);
            }
        });
        return select;
    };

    // Create a queryindex select menu
    $.querywidget.createQueryIndex = function (value) {
        return $.querywidget.createSelect($.querywidget.config.indexes,
                            value,
                            'queryindex',
                            'query.i:records');
    };

    // Create a queryoperator select menu
    $.querywidget.createQueryOperator = function (index, value) {
        return $.querywidget.createSelect($.querywidget.config.indexes[index].operators,
                            value,
                            'queryoperator',
                            'query.o:records');
    };

    $.querywidget.createWidget = function (type, index) {
        switch (type) {
            case 'StringWidget':
                return $(document.createElement('input'))
                    .attr({
                        'autocomplete': 'off',
                        'type': 'text',
                        'name': 'query.v:records'
                    })
                    .addClass('querywidget queryvalue stringWidget');
                break;
            case 'DateWidget':
                return $(document.createElement('input'))
                    .attr({
                        'autocomplete': 'off',
                        'type': 'text',
                        'name': 'query.v:records'
                    })
                    .addClass('querywidget queryvalue dateWidget');
                break;
            case 'DateRangeWidget':
                return $(document.createElement('div'))
                    .addClass('querywidget dateRangeWidget')
                    .append($(document.createElement('input'))
                        .attr({
                            'autocomplete': 'off',
                            'type': 'text',
                            'name': 'query.v:records:list'
                        })
                        .addClass('queryvalue')
                    )
                    .append($(document.createElement('span'))
                        .html(' and ')
                    )
                    .append($(document.createElement('input'))
                        .attr({
                            'autocomplete': 'off',
                            'type': 'text',
                            'name': 'query.v:records:list'
                        })
                        .addClass('queryvalue')
                    )
                break;
            case 'ReferenceWidget':
                return $(document.createElement('dl'))
                    .addClass('querywidget referenceWidget')
                    .append($(document.createElement('dt'))
                        .html('Select...')
                        .addClass('hiddenStructure')
                    )
                    .append($(document.createElement('dd'))
                        .append($(document.createElement('input'))
                            .attr({
                                'autocomplete': 'off',
                                'type': 'text',
                                'name': 'query.v:records'
                            })
                            .addClass('queryvalue')
                        )
                    )
                break;
            case 'RelativePathWidget':
                return $(document.createElement('input'))
                    .attr({
                        'autocomplete': 'off',
                        'type': 'text',
                        'name': 'query.v:records'
                    })
                    .addClass('querywidget queryvalue relativePathWidget');
                break;
            case 'MultipleSelectionWidget':
                var dl = $(document.createElement('dl'))
                    .addClass('querywidget multipleSelectionWidget')
                    .append($(document.createElement('dt'))
                        .append($(document.createElement('span'))
                            .html('Select...')
                        )
                        .append($(document.createElement('span'))
                            .addClass('arrowDownAlternative')
                            .html('&#09660;')
                        )
                    )
                var dd = $(document.createElement('dd')).addClass('hiddenStructure widgetPulldownMenu')
                $.each($.querywidget.config.indexes[index].values, function (i, val) {
                    dd.append($(document.createElement('label'))
                        .append($(document.createElement('input'))
                            .attr({
                                'type': 'checkbox',
                                'name': 'query.v:records:list',
                                'value': i
                            })
                        )
                        .append($(document.createElement('span'))
                            .html(val.title)
                        )
                    )
                });
                dl.append(dd);
                return dl;
                break;
        }
    };

    $.querywidget.getCurrentWidget  = function (node) {
        var classes = node.attr('class').split(' ');
        for (i in classes) {
            if (classes[i].indexOf('Widget') != -1) {
                var classname = classes[i];
                return classname.slice(0,1).toUpperCase() + classname.slice(1);
            }
        }
    };

    $.querywidget.updateSearch = function () {
        var query = portal_url + "/@@querybuilder_html_results?";
        var querylist  = [];
        $('.ArchetypesQueryWidget .queryindex').each(function () {
            var results = $(this).parents('.criteria').children('.queryresults');
            var index = $(this).val();
            var operator = $(this).parents('.criteria').children('.queryoperator').val();
            var widget = $.querywidget.config.indexes[index].operators[operator].widget;
            querylist.push('query.i:records=' + index);
            querylist.push('query.o:records=' + operator);
            switch (widget) {
                case 'DateRangeWidget':
                    var querywidget = $(this).parents('.criteria').find('.querywidget');
                    querylist.push('query.v:records:list=' + $(querywidget.children('input')[0]).val());
                    querylist.push('query.v:records:list=' + $(querywidget.children('input')[1]).val());
                    break;
                case 'MultipleSelectionWidget':
                    var querywidget = $(this).parents('.criteria').find('.querywidget');
                    querywidget.find('input:checked').each(function () {
                        querylist.push('query.v:records:list=' + $(this).val());
                    });
                    break;
                default:
                    querylist.push('query.v:records=' + $(this).parents('.criteria').find('.queryvalue').val());
                    break;
            }

            $.get(portal_url + '/@@querybuildernumberofresults?' + querylist.join('&'),
                  {},
                  function (data) { results.html(data); });
        });
        query += querylist.join('&');
        query += '&sort_on=' + $('#sort_on').val();
        if ($('#sort_order:checked').length > 0) {
            query += '&sort_order=reverse'
        }
        $.get(query, {}, function (data) { $('.ArchetypesQueryWidget .previewresults').html(data); });
    };

    // Enhance for javascript browsers
    $(document).ready(function () {

        // Init
        $.querywidget.init();


    });

    // Init widget
    $.querywidget.init = function () {

        // Check if already initialized
        if ($.querywidget.initialized == true) {

            // Return nothing done
            return false;
        }

        // Set initialized
        $.querywidget.initialized = true;

        // Get configuration
        $.getJSON(portal_url + '/@@querybuilderjsonconfig', function (data) {
            $.querywidget.config = data;

            // Find querywidgets
            $(".ArchetypesQueryWidget").each(function () {

                // Get object
                var obj = $(this);

                // Hide controls used for non-javascript only
                obj.find(".addIndexButton").hide();
                obj.find(".multipleSelectionWidget dt").removeClass('hiddenStructure');
                obj.find(".multipleSelectionWidget dd").addClass('hiddenStructure widgetPulldownMenu');

                $('div.queryindex').each(function () {
                    $(this).before(
                        $(document.createElement('div'))
                            .addClass('queryresults discreet')
                            .html('')
                    )
                    $(this).replaceWith($.querywidget.createQueryIndex($(this).children('input').val()));
                });
                $('div.queryoperator').each(function () {
                    $(this).replaceWith($.querywidget.createQueryOperator($(this).parents('.criteria').children('.queryindex').val(),
                                                            $(this).children('input').val()));
                });
                $.querywidget.updateSearch();
            });
        });

        $('.multipleSelectionWidget dt').live('click', function () {
            if ($(this).parent().children('dd').hasClass('hiddenStructure')) {
                $(this).parent().children('dd').removeClass('hiddenStructure');
            } else {
                $(this).parent().children('dd').addClass('hiddenStructure');
            }
        });

        $('.queryindex').live('change', function () {
            var index = $(this).find(':selected')[0].value;
            $(this).parents(".criteria").children('.queryoperator')
                .replaceWith($.querywidget.createQueryOperator(index, ''));
            var operatorvalue = $(this).parents('.criteria').children('.queryoperator').val();
            var widget = $.querywidget.config.indexes[index].operators[operatorvalue].widget;
            var querywidget = $(this).parent(".criteria").children('.querywidget');
            if ((widget != $.querywidget.getCurrentWidget(querywidget)) || (widget == 'MultipleSelectionWidget')) {
                querywidget.replaceWith($.querywidget.createWidget(widget, index));
            }
            $.querywidget.updateSearch();
        });

        $('.queryoperator').live('change', function () {
            var index = $(this).parents('.criteria').children('.queryindex').val();
            var operatorvalue = $(this).children(':selected')[0].value;
            var widget = $.querywidget.config.indexes[index].operators[operatorvalue].widget;
            var querywidget = $(this).parent().children('.querywidget');
            if (widget != $.querywidget.getCurrentWidget(querywidget)) {
                querywidget.replaceWith($.querywidget.createWidget(widget, index));
            }
            $.querywidget.updateSearch();
        });

        $('#sort_on,#sort_order,.multipleSelectionWidget input').live('change', function () {
            $.querywidget.updateSearch();
        });

        $('.queryvalue').live('keyup', function () {
            $.querywidget.updateSearch();
        });

        $('.queryvalue').live('keydown', function (e) {
            if (e.keyCode == 13) {
                return false;
            }
        });

        $('.addIndex').live('change', function () {
            var index = $(this).children(':selected')[0].value;
            var criteria = $(this).parents('.criteria');
            var newcriteria = $(document.createElement('div'))
                                .addClass('criteria');

            newcriteria.append(
                    $(document.createElement('div'))
                        .addClass('queryresults discreet')
                        .html('')
                )
            newcriteria.append($.querywidget.createQueryIndex(index));
            var operator = $.querywidget.createQueryOperator(index,'');
            newcriteria.append(operator);
            var operatorvalue = $(operator.children()[0]).attr('value');
            newcriteria.append($.querywidget.createWidget($.querywidget.config.indexes[index].operators[operatorvalue].widget, index));
            newcriteria.append(

                // How will we translate these values?

                $(document.createElement('input'))
                    .attr({
                        'value': 'Remove term',
                        'type': 'submit',
                        'name': 'removecriteria'
                    })
                    .addClass('removecriteria discreet')
            )
            criteria.before(newcriteria);
            $(this).val('');
            $.querywidget.updateSearch();
        });

        $('.removecriteria').live('click', function () {
            $(this).parents('.criteria').remove();
            $.querywidget.updateSearch();
            return false;
        });
    };
})(jQuery);
