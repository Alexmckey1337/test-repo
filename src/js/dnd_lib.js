/*let dragSrcEl = null; //Элемент который будем перетаскивать 
function handleDragStart(e) {
 // this.style.opacity = '0.4';  // this / e.target is the source node.
  dragSrcEl = this;

  //dragSrcEl.style.display ='none'
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault(); // Necessary. Allows us to drop.
  }

  e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.
  //console.log(e.currentTarget)
  return false;
}

function handleDragEnter(e) {
  // this / e.target is the current hover target.
  this.classList.add('over');
 // this.style.marginBottom = '100px'
}

function handleDragLeave(e) {
  this.classList.remove('over');  // this / e.target is previous target element.
  //this.style.marginBottom = '0px'
}

function handleDrop(e) {
  // this / e.target is current target element.

  if (e.stopPropagation) {
    e.stopPropagation(); // stops the browser from redirecting.
  }

 let html = e.currentTarget.innerHTML;
 
  e.currentTarget.innerHTML = dragSrcEl.innerHTML;
  dragSrcEl.innerHTML = html
  
  // See the section on the DataTransfer object.
 //e.currentTarget.parentElement.insertBefore(  dragSrcEl, e.currentTarget.nextElementSibling )
  return false;
}

function handleDragEnd(e) {
  // this/e.target is the source node.

 Array.prototype.forEach.call(cols, function (col) {
    col.classList.remove('over');
  });

}
*/