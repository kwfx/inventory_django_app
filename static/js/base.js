function main() {

  $(document).ready(function () {
    var bootstrapButton = $.fn.button.noConflict() // return $.fn.button to previously assigned value
    $.fn.bootstrapBtn = bootstrapButton
    $.widget.bridge('uitooltip', $.ui.tooltip);
    $('.add-lotline').click(_addLotLine);
    $.widget("custom.combobox", {
      _create: function () {
        this.wrapper = $("<span>")
          .addClass("custom-combobox d-flex")
          .insertAfter(this.element);
        this.element.hide();
        this._createAutocomplete();
        this._createShowAllButton();
      },

      _createAutocomplete: function () {
        var selected = this.element.children(":selected"),
          value = selected.val() ? selected.text() : "";

        this.input = $("<input>")
          .appendTo(this.wrapper)
          .val(value)
          .attr("title", "")
          .addClass("custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left  form-control")
          .autocomplete({
            delay: 0,
            minLength: 0,
            source: this._source.bind(this),
          })
          .tooltip({
            classes: {
              "ui-tooltip": "ui-state-highlight"
            }
          });
        this._on(this.input, {
          autocompleteselect: function (event, ui) {
            ui.item.option.selected = true;
            this._trigger("select", event, {
              item: ui.item.option
            });
            this._onProductSelected();
          },
          autocompletechange: "_removeIfInvalid"
        });
      },
      _source: async function (request, response) {
        let res = await fetch(`${window.location.origin}/inventory/product-autocomplete/?term=${request.term}`)
        let data = await res.json()
        response(this.element.children("option").map(function () {
          var text = $(this).text();
          if (this.value && data.indexOf(this.value) != -1)
            return {
              label: text,
              value: text,
              option: this
            };
        }))
      },
      _createShowAllButton: function () {
        var input = this.input,
          wasOpen = false;

        $("<a>")
          .attr("tabIndex", -1)
          .attr("title", "Show All Items")
          .tooltip()
          .appendTo(this.wrapper)
          .removeClass("ui-corner-all")
          .addClass("custom-combobox-toggle ui-corner-right fa fa-caret-down text-decoration-none")
          .on("mousedown", function () {
            wasOpen = input.autocomplete("widget").is(":visible");
          })
          .on("click", function () {
            input.trigger("focus");
            // Close if already visible
            if (wasOpen) {
              return;
            }
            // Pass empty string as value to search for, displaying all results
            input.autocomplete("search", "");
          });
      },

      _removeIfInvalid: function (event, ui) {
        // Selected an item, nothing to do
        if (ui.item) {
          return;
        }
        // Search for a match (case-insensitive)
        var value = this.input.val(),
          valueLowerCase = value.toLowerCase(),
          valid = false;
        this.element.children("option").each(function () {
          if ($(this).text().toLowerCase() === valueLowerCase) {
            this.selected = valid = true;
            return false;
          }
        });
        // Found a match, nothing to do
        if (valid) {
          return;
        }
        // Remove invalid value
        this.input
          .val("")
          .attr("title", value + " didn't match any item")
          .tooltip("show");
        this.element.val("");
        this._delay(function () {
          this.input.tooltip("hide").attr("title", "");
        }, 2500);
        this.input.autocomplete("instance").term = "";
      },

      _destroy: function () {
        this.wrapper.remove();
        this.element.show();
      },
            
      _onProductSelected: function(){
        let $select = this.element;
        $product_line = $select.parents(".product");
        $search_input = $product_line.find(".search_input");
        let product_id = $select.val();
        if (!product_id) {
          $select.val('');
          return
        }
        $.ajax({
          url: "/inventory/product_details/" + product_id,
          type: 'GET',
        }).done((res) => {
          if (res.length) {
            let existing = $(".inventory_form").find(".product_field select").filter((i, e) => ($(e).val() == res[0].pk && e !== $select[0])).length
            if (existing) {
              this.input.val('');
              $select.val('');
              $product_line.find("input").val('')
              Swal.fire({
                position: "top",
                icon: "warning",
                title: `L'article [${res[0].fields.designation}] a été déjà compté`,
                showConfirmButton: false,
                timer: 3000,
              });
            } else {
              $product_line.find(".product_field select").val(res[0].pk);
              $product_line.find(".product_internal_ref input").val(res[0].fields.internal_ref);
              $product_line.find(".product_designation input").val(res[0].fields.designation);
              $product_line.find(".product_uom_sale input").val(res[0].fields.sale_uom);
              $product_line.find(".product_supplier input").val(res[0].fields.supplier);
            }
          }
        }).fail((err) => console.log(err.responseText))
      }
    });
    $(".product-line").find('.product_field select').combobox();
  })
};

function _addLotLine(ev) {
  ev.preventDefault();
  target = $(ev.target);
  let product_line = target.closest(".product-line")
  var count = product_line.find(".lot-line").length;
  var tmplMarkup = product_line.find('#lotline-template').html();
  var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
  product_line.find('.lot-lines').append(compiledTmpl);
  product_line.find('input[id*="TOTAL_FORMS"]').attr('value', count + 1);
};

function _onClickDeleteLine(event) {
  event.preventDefault();
  Swal.fire({
    title: "Etes vous sûr ?",
    text: "",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    cancelButtonText: "Annuler",
    confirmButtonText: "Oui, Supprimer !"
  }).then((result) => {
    if (result.isConfirmed) {
      target = $(event.target);
      let line = target.closest("tr.lot-line")
      if (!line.length) {
        line = target.closest("div.product-line")
      }
      line.hide()
      line.find('input[id*="DELETE"]').prop("checked", true);
    }
  });
  return
}

function _searchform_onchange_zone(e) {
  target = $(e.target);
  $form = target.parents("form")
  $form.find("#id_num_inv").val("").change();
}

function _onChangeCompareFormZone(e) {
  target = $(e.target);
  $form = target.parents("form")
  $form.find("#id_inventory_1").val("").change();
  $form.find("#id_inventory_2").val("").change();
}

function _seachform_clear(e) {
  target = $(e.target);
  $form = target.parents("form")
  $form.find("#id_product_ref").val('');
  $form.find("#id_zone").val('').change();
}

function _onClickDeleteRecord(model_name, product_id) {
  Swal.fire({
    title: "Etes vous sûr ?",
    text: "",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    cancelButtonText: "Annuler",
    confirmButtonText: "Oui, Supprimer !"
  }).then((result) => {
    if (result.isConfirmed) {
      fetch("/inventory/delete/" + model_name + "/" + product_id).then(() => { location.reload() })
    }
  });
  return
}

function _onClickImportStock(event) {
  fetch("/inventory/stock/import").then((html_data) => {
    html_data.text().then((res) => {
      Swal.fire({
        title: false,
        position: "top",
        text: "",
        html: res,
        icon: false,
        showCancelButton: false,
        showConfirmButton: true,
        confirmButtonText: "Importer"
      }).then((result) => {
        if (result.isConfirmed) {
          const form = $(".stock_import_form form")[0];
          const formData = new FormData(form);
          fetch("/inventory/stock/import", {
            method: 'POST',
            body: formData
          }).then((response) => {
            if (response.ok) {
              location.href = response.url;
            } else {
              response.text().then((error) => {
                Swal.fire({
                  position: "top",
                  text: error,
                  icon: "error",
                  showCancelButton: false,
                  showConfirmButton: true,
                  confirmButtonText: "Ok"
                })
              })
            }
          })
        }
      })
    })

  })
};

_onChangeSystemQty = function (event) {
  let $input = $(event.target);
  let $line = $input.parents(".inv-line")
  let ecart = parseFloat($line.find('.qty-inv').text()) - parseFloat($input.val())
  $line.find('.stock-ecart').text(Number(ecart).toFixed(2))
  if (parseFloat($input.val()) != parseFloat($input.attr("value"))) {
    $line.attr("changed", true);
  } else {
    $line.attr("changed", false)
  }
  if (ecart) {
    $line.find('.stock-ecart').addClass("text-danger");
  } else {
    $line.find('.stock-ecart').removeClass("text-danger");
  }
  if ($(".stockcomparison-listview .inv-line[changed=true]").length) {
    $(".stockcomparison-listview .btn-success").show()
  } else {
    $(".stockcomparison-listview .btn-success").hide()
  }
};

function _onClickUpdateStock(event) {
  let data = {}
  $(".stockcomparison-listview .inv-line[changed=true]").each((i, e) => {
    let lotline_id = $(e).attr("lot-line-id");
    let stockline_id = $(e).attr("stock-line-id");
    let qty_system = $(e).find(".qty-sys").val()
    data[lotline_id] = { stockline_id, qty_system }
  });
  let csrfmiddlewaretoken = $(".stockcomparison-listview").find("input[name=csrfmiddlewaretoken]").val()
  fetch(location.href, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      "X-CSRFToken": csrfmiddlewaretoken,
      "Content-Type": "application/json"
    },
  }).then((response) => {
    if (response.ok) {
      location.href = response.url;
    } else {
      response.text().then((error) => {
        Swal.fire({
          position: "top",
          text: error,
          icon: "error",
          showCancelButton: false,
          showConfirmButton: true,
          confirmButtonText: "Ok"
        })
      })
    }
  })
};

function _onClickinventoryAction(action, model=''){
  let dateToday = new Date().toISOString().slice(0, 10)
  let inv_ids = $('.inventory-list .inv-line-checkbox:checked').map((i ,e) => $(e).attr("data-id")).toArray()
  let csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val()
  if (action == 'delete'){
    let allproms = inv_ids.reduce((proms, inv_id) => proms.concat([fetch("/inventory/delete/inventory/" + inv_id)]), [])
    Promise.all(allproms).then(() => { location.reload()})
  }
  if (action == 'compare' && inv_ids.length >= 2){
    location.href = `${window.location.origin}/inventory/compare?inventory_1=${inv_ids[0]}&inventory_2=${inv_ids[1]}`
  }
  if (action == 'export'){
    if (!inv_ids.length){
      inv_ids = $('.inventory-list .inv-line-checkbox').map((i ,e) => $(e).attr("data-id")).toArray()
    }
    if (model == 'inventory-compare'){
      inv_ids = inv_ids.concat([
        $("#id_inventory_1").val(),
        $("#id_inventory_2").val(),
      ])
    }
    data = {
      ids: inv_ids
    }
    fetch(`${window.location.origin}/inventory/export/${model}`, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        "X-CSRFToken": csrfmiddlewaretoken,
        "Content-Type": "application/json"
      },
    }).then(response => {
      return response.blob()
    })
    .then(response => {
        const blob = new Blob([response], {type: response.type});
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${model}-${dateToday}.xlsx`;
        document.body.appendChild(a);
        a.click();
    })
  }
}

main();