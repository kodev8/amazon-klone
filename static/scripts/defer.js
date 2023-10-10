handleCustomInputs();

// resize dropsown when selected then focus search bar

var selectId = document.getElementById("search-cat");

function updateSelect(){
  var selectedText = selectId.options[selectId.selectedIndex].text;
  selectId.style.width = 30 + (selectedText.length * 8) + "px";
  let searchBar = document.querySelector('#search-bar')
  searchBar.focus()

  // https://stackoverflow.com/questions/511088/use-javascript-to-place-cursor-at-end-of-text-in-text-input-element
  
searchBar.setSelectionRange(-1, -1)

}

if (selectId){
selectId.addEventListener('load', updateSelect)
selectId.onchange=updateSelect

}


function handleMiniImages()
// image on product 
{let main_img = document.querySelector('#main-img');
if (main_img){
    var main_src = main_img.src

    let images = document.querySelectorAll('.mini-img')
    images.forEach(img => {
        img.addEventListener('mouseover', ()=>main_img.src = img.src)
        img.addEventListener('mouseout', ()=>main_img.src = main_src)
        img.addEventListener('click', ()=> {
            main_img.src = img.src
            main_src = img.src
            images.forEach(innerImg =>{
                if(innerImg != img){
                    innerImg.classList.remove("border-orange-300")

                }
                })
            img.classList.remove('border-slate-300')
            img.classList.add('border-orange-300')
            })
        
    })
  }
}

handleMiniImages()

function handleShowRatings () { 

  let ratings = document.querySelectorAll('.rating-container')
  ratings.forEach(rating => linkhHoverShow(rating, rating.querySelector('.rating')))
}
handleShowRatings()


// =========================================================
var textareas= document.querySelectorAll('textarea')

// Function to resize the textarea based on its content
function resizeTextarea(event) {
event.target.style.minHeight = 'auto'
event.target.style.minHeight = `${event.target.scrollHeight}px`;
}

// Listen for input events (typing)
textareas.forEach(textarea => textarea.addEventListener('input', resizeTextarea));

function handleTextAreas() {
  var textareas= document.querySelectorAll('textarea')

// Function to resize the textarea based on its content
function resizeTextarea(event) {
event.target.style.minHeight = 'auto'
event.target.style.minHeight = `${event.target.scrollHeight}px`;
}

// Listen for input events (typing)
textareas.forEach(textarea => textarea.addEventListener('input', resizeTextarea));

}


