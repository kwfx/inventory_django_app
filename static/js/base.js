function main(){
    console.log("HERE WE ARE !!!")
    $(document).ready(function() {
        // when user clicks add more btn of lines
          $('.add-lines').click(function(ev) {
              ev.preventDefault();
              var count = $('#item-lines').children().length;
              var tmplMarkup = $('#lines-template').html();
              var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
              $('#item-lines').append(compiledTmpl);
              $('#id_lines-TOTAL_FORMS').attr('value', count+1);
          });
      });
};

function onSearchKeyUp(event){
    if (event.key != 'Backspace') {
        event.target.parentElement.submit()
    }
};
main();