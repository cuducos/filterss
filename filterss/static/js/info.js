$(document).ready(function(){

    $("#bookmark").click(function(e){

        e.preventDefault();
        var url = document.URL;
        var title = document.title;
        var is_chrome = window.chrome

        // mozilla
        if ( !is_chrome && window.sidebar ) {
            window.sidebar.addPanel(title, url,"");
        
        // ie
        } else if( !is_chrome && ( window.external || document.all ) ) {
            window.external.AddFavorite( url, title);
        
        // opera
        } else if( !is_chrome && window.opera ) {
            $("#bookmark").attr("href",url);
            $("#bookmark").attr("title",title);
            $("#bookmark").attr("rel","sidebar");
        
        } else {
            alert('Your browser does not support this bookmark action. Please, use the browser menu to add your bookmark.');
            return false;
        }
  });

});
