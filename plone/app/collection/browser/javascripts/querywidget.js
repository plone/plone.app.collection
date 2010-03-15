;(function($) {

    // Search config
    var plone_app_search_config = {};

    // Create a select menu
    function CreateSelect(values, selectedvalue, className, name) {
        // Create select
        var select = $(document.createElement('select'))
                            .addClass(className)
                            .attr('name', name)
        $.each(values, function (i, val) {
            var option = $(document.createElement('option'))
                            .attr('value', i)
                            .html(val.friendly_name)
            if (i == selectedvalue) {
                option.attr('selected', 'selected');
            }
            select.append(option);
        });
        return select;
    }

    // Create a queryindex select menu
    function CreateQueryIndex(value) {
        return CreateSelect(plone_app_search_config.indexes,
                            value,
                            'queryindex',
                            'query.i:records');
    }

    // Create a queryoperator select menu
    function CreateQueryOperator(index, value) {
        return CreateSelect(plone_app_search_config.indexes[index].operators,
                            value,
                            'queryoperator',
                            'query.o:records');
    }

    function CreateWidget(type, index) {
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
                            .html('▼')
                        )
                    )
                var dd = $(document.createElement('dd')).addClass('hiddenStructure')
                $.each(plone_app_search_config.indexes[index].values, function (i, val) {
                    dd.append($(document.createElement('label'))
                        .append($(document.createElement('input'))
                            .attr({
                                'type': 'checkbox',
                                'name': 'query.v:records:list',
                                'value': i
                            })
                        )
                        .append($(document.createElement('span'))
                            .html(val.friendly_name)
                        )
                    )
                });
                dl.append(dd);
                return dl;
                break;
        }
    }

    // Enhance for javascript browsers
    $(document).ready(function () {

        $("#advancedsearch").each(function () {

            // Hide controls used for non-javascript only
            $(".addIndexButton").hide();
            $(".multipleSelectionWidget dt").removeClass('hiddenStructure');
            $(".multipleSelectionWidget dd").addClass('hiddenStructure widgetPulldownMenu');

            $.getJSON('querybuilderjsonconfig', function (data) {
                plone_app_search_config = data;
                $('div.queryindex').each(function () {
                    $(this).before(
                        $(document.createElement('div'))
                            .addClass('queryresults discreet')
                            .html('')
                    )
                    $(this).replaceWith(CreateQueryIndex($(this).children('input').val()));
                });
                $('div.queryoperator').each(function () {
                    $(this).replaceWith(CreateQueryOperator($(this).parents('.field').children('.queryindex').val(),
                                                            $(this).children('input').val()));
                });
                UpdateSearch();
            });
        });
    });

    function GetCurrentWidget (node) {
        var classes = node.attr('class').split(' ');
        for (i in classes) {
            if (classes[i].indexOf('Widget') != -1) {
                var classname = classes[i];
                return classname.slice(0,1).toUpperCase() + classname.slice(1);
            }
        }
    }

    $('.multipleSelectionWidget dt').live('click', function () {
        if ($(this).parent().children('dd').hasClass('hiddenStructure')) {
            $(this).parent().children('dd').removeClass('hiddenStructure');
        } else {
            $(this).parent().children('dd').addClass('hiddenStructure');
        }
    });

    $('.queryindex').live('change', function () {
        var index = $(this).children(':selected')[0].value;
        $(this).parent().children('.queryoperator')
            .replaceWith(CreateQueryOperator(index, ''));
        var operatorvalue = $(this).parents('.field').children('.queryoperator').val();
        var widget = plone_app_search_config.indexes[index].operators[operatorvalue].widget;
        var querywidget = $(this).parent().children('.querywidget');
        if ((widget != GetCurrentWidget(querywidget)) || (widget == 'MultipleSelectionWidget')) {
            querywidget.replaceWith(CreateWidget(widget, index));
        }
        UpdateSearch();
    });

    $('.queryoperator').live('change', function () {
        var index = $(this).parents('.field').children('.queryindex').val();
        var operatorvalue = $(this).children(':selected')[0].value;
        var widget = plone_app_search_config.indexes[index].operators[operatorvalue].widget;
        var querywidget = $(this).parent().children('.querywidget');
        if (widget != GetCurrentWidget(querywidget)) {
            querywidget.replaceWith(CreateWidget(widget, index));
        }
        UpdateSearch();
    });

    $('#sort_on,#sort_order,.multipleSelectionWidget input').live('change', function () {
        UpdateSearch();
    });

    $('.queryvalue').live('keyup', function () {
        UpdateSearch();
    });
    $('.queryvalue').live('keydown', function (e) {
        if (e.keyCode == 13) {
            return false;
        }
    });

    $('.addIndex').live('change', function () {
        var index = $(this).children(':selected')[0].value;
        var field = $(this).parents('.field');
        var newfield = $(document.createElement('div'))
                            .addClass('field');

        newfield.append(
                $(document.createElement('div'))
                    .addClass('queryresults discreet')
                    .html('')
            )
        newfield.append(CreateQueryIndex(index));
        var operator = CreateQueryOperator(index,'');
        newfield.append(operator);
        var operatorvalue = $(operator.children()[0]).attr('value');
        newfield.append(CreateWidget(plone_app_search_config.indexes[index].operators[operatorvalue].widget, index));
        newfield.append(
            $(document.createElement('input'))
                .attr({
                    'value': 'Remove criterion',
                    'type': 'submit',
                    'name': 'removecriteria'
                })
                .addClass('removecriteria discreet')
        )
        field.before(newfield);
        $(this).val('');
        UpdateSearch();
    });

    $('.removecriteria').live('click', function () {
        $(this).parents('.field').remove();
        UpdateSearch();
        return false;
    });

    function UpdateSearch() {
        var query = "querybuilderpreviewresults?";
        var querylist  = [];
        $('#advancedsearch .queryindex').each(function () {
            var results = $(this).parents('.field').children('.queryresults');
            var index = $(this).val();
            var operator = $(this).parents('.field').children('.queryoperator').val();
            var widget = plone_app_search_config.indexes[index].operators[operator].widget;
            querylist.push('query.i:records=' + index);
            querylist.push('query.o:records=' + operator);
            switch (widget) {
                case 'DateRangeWidget':
                    var querywidget = $(this).parents('.field').find('.querywidget');
                    querylist.push('query.v:records:list=' + $(querywidget.children('input')[0]).val());
                    querylist.push('query.v:records:list=' + $(querywidget.children('input')[1]).val());
                    break;
                case 'MultipleSelectionWidget':
                    var querywidget = $(this).parents('.field').find('.querywidget');
                    querywidget.find('input:checked').each(function () {
                        querylist.push('query.v:records:list=' + $(this).val());
                    });
                    break;
                default:
                    querylist.push('query.v:records=' + $(this).parents('.field').find('.queryvalue').val());
                    break;
            }

            $.get('querybuildernumberofresults?' + querylist.join('&'),
                  {},
                  function (data) { results.html(data); });
        });
        query += querylist.join('&');
        query += '&sort_on=' + $('#sort_on').val();
        if ($('#sort_order:checked').length > 0) {
            query += '&sort_order=reverse'
        }
        $.get(query, {}, function (data) { $('#advancedsearch .previewresults').html(data); });
    }

})(jQuery);
