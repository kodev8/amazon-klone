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

panel()
    