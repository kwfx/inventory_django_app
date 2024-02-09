function main(){
    
    $(document).ready(function() {
        var bootstrapButton = $.fn.button.noConflict() // return $.fn.button to previously assigned value
        $.fn.bootstrapBtn = bootstrapButton 
        $.widget.bridge('uitooltip', $.ui.tooltip);
        $('.add-lotline').click(_addLotLine);
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
  product_line.find('input[id*="TOTAL_FORMS"]').attr('value', count+1);
};

function _onClickDeleteLine(event){
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
        if (!line.length){
          line = target.closest("div.product-line")
        }
        line.hide()
        line.find('input[id*="DELETE"]').prop("checked", true);
      }
    });
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

function _onClickSearchProduct(e){
  e.preventDefault();
  target = $(e.target);
  $product_line = target.parents(".product");
  $search_input = $product_line.find(".search_input");
  let old_ref = $search_input.val();
  if (!old_ref){
    $product_line.find(".product_field select").val('');
    return
  }
  $.ajax({
    url: "/inventory/search_product_by_oldref/" + old_ref,
    type:'GET',
  }).done(function (res) {
      if (res.length){
        let existing = $(".inventory_form").find(".product_field select").filter((i, e) => $(e).val() == res[0].pk)
        if (existing){
          Swal.fire({
            position: "top",
            icon: "warning",
            title: `L'article [${res[0].fields.designation}] a été déjà compté`,
            showConfirmButton: false,
            timer: 3000,
          });
        }else{
          $product_line.find(".product_field select").val(res[0].pk);
          $product_line.find(".product_internal_ref input").val(res[0].fields.internal_ref);
          $product_line.find(".product_designation input").val(res[0].fields.designation);
          $product_line.find(".product_uom_sale input").val(res[0].fields.sale_uom);
          $product_line.find(".product_supplier input").val(res[0].fields.supplier);
        }
      }else{
        $product_line.find(".product_field select").val('');
        $product_line.find("input:not('.search_input')").val("---------");
        Swal.fire({
          position: "top",
          icon: "warning",
          title: "Article introuvable",
          showConfirmButton: false,
          timer: 3000
        });
      }
  }).fail((err) => console.log(err.responseText))
}

function _onClickDeleteRecord(model_name, product_id){
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
      fetch("/inventory/delete/" + model_name + "/" + product_id).then(() => {location.reload()})
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
            if (response.ok){
              location.href = response.url;
            }else {
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

_onChangeSystemQty = function(event){
  let $input = $(event.target);
  let $line = $input.parents(".inv-line")
  let ecart = parseFloat($line.find('.qty-inv').text()) - parseFloat($input.val())
  $line.find('.stock-ecart').text(Number(ecart).toFixed(2))
  if (parseFloat($input.val()) != parseFloat($input.attr("value"))){
    $line.attr("changed", true);
  }else{
    $line.attr("changed", false)
  }
  if (ecart){
    $line.find('.stock-ecart').addClass("stock-ecart-red");
  }else{
    $line.find('.stock-ecart').removeClass("stock-ecart-red");
  }
  if ($(".stockcomparison-listview .inv-line[changed=true]").length){
    $(".stockcomparison-listview .btn-success").show()
  }else{
    $(".stockcomparison-listview .btn-success").hide()
  }
};

function _onClickUpdateStock(event){
  let data = {}
  $(".stockcomparison-listview .inv-line[changed=true]").each((i, e) => {
    let lotline_id = $(e).attr("lot-line-id");
    let stockline_id = $(e).attr("stock-line-id");
    let qty_system = $(e).find(".qty-sys").val()
    data[lotline_id] = {stockline_id, qty_system}
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
    if (response.ok){
      location.href = response.url;
    }else {
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
main();