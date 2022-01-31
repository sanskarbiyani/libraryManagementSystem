function changeForm(elem){
    if(elem.classList.contains("active")===false){
        var registerForm = document.forms.registerForm;
        var loginForm = document.forms.loginForm;
        if(elem == elem.parentElement.firstElementChild){
            elem.parentElement.firstElementChild.classList.add("active");
            elem.parentElement.lastElementChild.classList.remove("active");
            registerForm.classList.add("hiddenForm");
            loginForm.classList.remove("hiddenForm");
        } else {
            elem.parentElement.lastElementChild.classList.add("active");
            elem.parentElement.firstElementChild.classList.remove("active");
            registerForm.classList.remove("hiddenForm");
            loginForm.classList.add("hiddenForm");
        }
    }
}