import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1440,height:1000}});
try{
  await page.goto('http://127.0.0.1:3000/cases/case-totes/conversations');
  await page.getByRole('button',{name:'Prepare enquiry',exact:true}).waitFor();
  await page.getByRole('button',{name:'Prepare enquiry',exact:true}).click();
  await page.getByRole('status').getByText(/Counteroffer prepared/).waitFor();
  await page.getByRole('button',{name:'Approve draft',exact:true}).click();
  await page.getByRole('status').getByText(/Exact draft approved/).waitFor();
  await page.getByRole('button',{name:'Send in demo',exact:true}).click();
  await page.getByText('Sent to demo supplier',{exact:true}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Send in demo',exact:true}).isEnabled(),false);
  await page.getByRole('button',{name:'Check demo reply',exact:true}).click();
  await page.getByRole('status').getByText(/Controlled reply saved/).waitFor();
  await page.getByText('Your approved enquiry',{exact:true}).waitFor();
  await page.screenshot({path:'test-results/outreach-desktop.png',fullPage:true});
  console.log('PASS: prepare, exact approval, one controlled send, supplier reply, consumed approval.');
}finally{await browser.close();}
