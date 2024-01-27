function main(){
    
    $(document).ready(function() {
        var bootstrapButton = $.fn.button.noConflict() // return $.fn.button to previously assigned value
        $.fn.bootstrapBtn = bootstrapButton 
        $.widget.bridge('uitooltip', $.ui.tooltip);
        $('.add-lotline').click(function(ev) {
            ev.preventDefault();
            target = $(ev.target);
            let product_line = target.closest(".product-line")
            var count = product_line.find(".lot-line").length;
            var tmplMarkup = product_line.find('#lotline-template').html();
            var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
            product_line.find('.lot-lines').append(compiledTmpl);
            product_line.find('input[id*="TOTAL_FORMS"]').attr('value', count+1);
        });
      $.widget("custom.combobox", {
        _create: function() {
          this.wrapper = $( "<span>" )
            .addClass( "custom-combobox" )
            .insertAfter( this.element );
   
          this.element.hide();
          this._createAutocomplete();
          this._createShowAllButton();
        },
   
        _createAutocomplete: function() {
          var selected = this.element.children( ":selected" ),
            value = selected.val() ? selected.text() : "";
   
          this.input = $( "<input>" )
            .appendTo( this.wrapper )
            .val( value )
            .attr( "title", "" )
            .addClass( "custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left" )
            .autocomplete({
              delay: 0,
              minLength: 0,
              source: window.location.origin + "/inventory/product-autocomplete",
            })
            .tooltip({
              classes: {
                "ui-tooltip": "ui-state-highlight"
              }
            });
   
          this._on( this.input, {
            autocompleteselect: function( event, ui ) {
              ui.item.option.selected = true;
              this._trigger( "select", event, {
                item: ui.item.option
              });
            },
   
            autocompletechange: "_removeIfInvalid"
          });
        },
   
        _createShowAllButton: function() {
          var input = this.input,
            wasOpen = false;
   
          $( "<a>" )
            .attr( "tabIndex", -1 )
            .attr( "title", "Show All Items" )
            .tooltip()
            .appendTo( this.wrapper )
            .button({
              icons: {
                primary: "ui-icon-triangle-1-s"
              },
              text: false
            })
            .removeClass( "ui-corner-all" )
            .addClass( "custom-combobox-toggle ui-corner-right" )
            .on( "mousedown", function() {
              wasOpen = input.autocomplete( "widget" ).is( ":visible" );
            })
            .on( "click", function() {
              input.trigger( "focus" );
   
              // Close if already visible
              if ( wasOpen ) {
                return;
              }
   
              // Pass empty string as value to search for, displaying all results
              input.autocomplete( "search", "" );
            });
        },
   
        _source: function( request, response ) {
          var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
          response( this.element.children( "option" ).map(function() {
            var text = $( this ).text();
            if ( this.value && ( !request.term || matcher.test(text) ) )
              return {
                label: text,
                value: text,
                option: this
              };
          }) );
        },
   
        _removeIfInvalid: function( event, ui ) {
   
          // Selected an item, nothing to do
          if ( ui.item ) {
            return;
          }
   
          // Search for a match (case-insensitive)
          var value = this.input.val(),
            valueLowerCase = value.toLowerCase(),
            valid = false;
          this.element.children( "option" ).each(function() {
            if ( $( this ).text().toLowerCase() === valueLowerCase ) {
              this.selected = valid = true;
              return false;
            }
          });
   
          // Found a match, nothing to do
          if ( valid ) {
            return;
          }
   
          // Remove invalid value
          this.input
            .val( "" )
            .attr( "title", value + " didn't match any item" )
            .tooltip( "open" );
          this.element.val( "" );
          this._delay(function() {
            this.input.tooltip( "close" ).attr( "title", "" );
          }, 2500 );
          this.input.autocomplete( "instance" ).term = "";
        },
   
        _destroy: function() {
          this.wrapper.remove();
          this.element.show();
        }
      });
      $(".product-line").find('tr.product select').combobox();
    })
};
function _onChangedProduct(event){
    let product_id = $(event.target).find("option:selected").val()
    if (!product_id){
        $("#id_product_supplier").empty().val('');
        return
    }
    $.ajax({
      url: "/inventory/get-product-data/" + product_id,
    }).done(function (res) {
        $("#id_product_supplier").empty().val(res[0].fields.supplier);
    }).fail((err) => console.log(err.responseText))
}

function _onClickDeleteInventory(inventory_id){
    $("#dialog-delete").find('.btn-confirm').attr('href', "/inventory/delete-inventory/" + inventory_id)
    $("#dialog-delete").modal('show');
}

function _onClickDeleteLine(event, inventory_line_id){
    const dialog_div = $("#dialog-delete")
    dialog_div.find('.btn-confirm').click(()=>{
        event.preventDefault();
        target = $(event.target);
        let line = target.closest("tr")
        line.hide()
        line.find('input[id*="DELETE"]').prop("checked", true);
        dialog_div.modal('hide');
    })
    dialog_div.modal('show');
    return
}

function _searchform_onchange_zone(e){
  target = $(e.target);
  $form = target.parents("form")
  $form.find("#id_num_inv").val("").change();
}
function _seachform_clear(e){
  target = $(e.target);
  $form = target.parents("form")
  $form.find("#id_product_ref").val('');
  $form.find("#id_zone").val('').change();
}
main();