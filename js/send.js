var send={
  name: 'saga', new_account: function(person, responseHandler){
    this.person=person; // remember person for logout
    var params="person="+ person;
    var xhr=new XMLHttpRequest();
    xhr.open('POST', this.baseUrl, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange=function(){
      if(this.readyState==4){
        responseHandler(this.status);        
      }
    }
    xhr.send(params);
  }
}
