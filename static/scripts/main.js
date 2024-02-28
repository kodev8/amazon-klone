function controlInputLength (e, maxlength) {
    let length = e.target.value.length
    if (length >= maxlength){
        e.target.value = e.target.value.slice(0, maxlength)

    }  
    formatted_length = e.target.value.length
    document.getElementById('count').innerHTML = formatted_length
}


function dth (event, target) {
    
    let t = event.target.querySelector(target)
    t.classList.toggle('hidden')

    document.addEventListener("click", (e) => {
    if (!event.target.contains(e.target)) {
        t.classList.add("hidden");
    }
    });
}
  
function clearCover(event) {
    event.target.remove()
    document.querySelector('#cover_photo img')?.remove(); 
    document.querySelector('#cover_check').value='default'
    // document.querySelector('#cover_path').value=''; 
}

//  links a given elleemtn to the item it shows on hover
function linkhHoverShow(element, to_hover) {

    // console.log(element, 'linked hover show', to_hover)
    element?.addEventListener('mouseenter', ()=>  {
        
        ht = setTimeout(()=>{
            to_hover?.classList.remove('invisible')
            element.focus()
    
    }, 700)

    } )

    element?.addEventListener('mouseleave', ()=> {

        if(!to_hover.matches(':hover')){
        clearTimeout(ht)
        to_hover?.classList.add('invisible')}
    })

    to_hover?.addEventListener('mouseleave', ()=> {

        if(!element.matches(':hover')){
        clearTimeout(ht)
        to_hover?.classList.add('invisible')}
    })

    let isMobile = false;

    element?.addEventListener('touchstart', () => {
        isMobile = true;
    });

    element?.addEventListener('click', (event) => {
        if (isMobile) {
            event.preventDefault()
            // Handle the click action for mobile devices
            if (to_hover.classList.contains('invisible')) {
                to_hover.classList.remove('invisible');
            } else {
                to_hover.classList.add('invisible');
            }
            isMobile = false; // Reset the flagcusto
        }
    });
    
}

// for selecting/deselecting all input
function select(how) {

    let cboxes = document.querySelectorAll('input[type=checkbox')
    try {
        if (how=='all'){
            cboxes.forEach(cbox => cbox.checked=true)
        }else if (how='none'){
            cboxes.forEach((cbox)=> cbox.checked=false)
        }
        
        return true
    }catch {
        return false
    }
}

// checking selecting a new cart quantity
function selectQty(event) {
    // console.log(event.target)

    if (isNaN(event.target.value)){
        // show update button
        if (event.target.value == '10+') htmx.ajax('GET', '/input-cart', {target:event.target.closest('div'),swap:'outerHTML'}) 
        return false
    }
    

    return true
}


function handleCustomInputs() {
    // console.log('exec')
    document.querySelectorAll('.custom-input-group')?.forEach(customInputGroup => {

        let customInput = customInputGroup.querySelector('.custom-input')
        customInput.addEventListener('input', (event) => {
            let inlineError = customInputGroup.querySelector('.inline-error')
            inlineError.innerHTML = ''
        })
      
        // let eye ico control if text input is password or text
        let eyeIcon = customInput.parentNode.querySelector('.eye-icon')
        if(eyeIcon){
          eyeIcon.addEventListener('click', (e)=> {
      
            e.preventDefault();
              if(customInput.type == 'password') {
                  eyeIcon.classList.remove('fa-eye-slash')
                  eyeIcon.classList.add('fa-eye')
                  customInput.type='text'
              }else {
                eyeIcon.classList.remove('fa-eye')
                eyeIcon.classList.add('fa-eye-slash')
                customInput.type='password'
      
              }
            })
          }
        })
}

function closeNotif(element) {

    element.closest('.notif')?.classList.remove('noti-open')
    element.closest('.notif')?.classList.add('noti-close')
}


function handleAddrAnonForm() {
      
let zip = document.querySelector('#zip_code')
let country = document.querySelector('#country')

zip.addEventListener('input',() => {country.querySelector('option').selected = true})
country.onchange = () => zip.value = ''

}

function openSideNav() {
    let sideNav = document.querySelector('#side-nav')
    let sideX =   document.querySelector('#side-x')
    let modalBg = document.querySelector('#modal-bg')
   document.querySelector('body').style.overflow='hidden'
    


    sideNav?.classList.remove('closed'); 
    sideX?.classList.remove('closed')
    modalBg?.classList.remove('hidden')
       modalBg.addEventListener('click', closeSideNav) 
}

function closeSideNav() {
    let sideNav = document.querySelector('#side-nav')
    let sideX =   document.querySelector('#side-x')
   document.querySelector('body').style.overflowY='auto'
   let modalBg = document.querySelector('#modal-bg')

    sideNav.classList.add('closed'); 
    modalBg.classList.add('hidden'); 
    sideX.classList.add('closed')
}

function checkSearchValue(event) {
    return event.target.value.trim() != ""
}

function toggleAll (element, ...classes) {
    classes.forEach(c => element.classList.toggle(c))
}


function panel() {

    const signin = document.querySelector('#nav-signin')
    const signinHover = document.querySelector('#nav-signin-hover')
    const icon = signin.querySelector('i')
    
      if (signin) {
        
        linkhHoverShow(signin, signinHover)
    
        signin.addEventListener('mouseenter', ()=>{
    
          let rect = icon.getBoundingClientRect()
          let swidth = parseFloat(getComputedStyle(signinHover).width )
    
          let arrowStyle = getComputedStyle(signinHover, ':after')
          let arrowHeight = parseFloat(arrowStyle.height)
    
          let iconwidth=parseFloat(getComputedStyle(icon).width)
    
          let arrowPlacement = rect.x
          signinHover.style.left = `${arrowPlacement -  swidth + swidth/4+ iconwidth/2}px`
          signinHover.style.top = `${rect.bottom + arrowHeight/4 - 2  }px`
    
        })
       
      }
  }
  